import dataclasses
from typing import Iterable, Optional, Callable, Union

import flashtext
import numpy as np
import spacy
import pandas as pd

from scattertext.contextual_embeddings.doc_splitter import doc_sentence_splitter
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc

from scattertext.OffsetCorpus import OffsetCorpus
from tqdm.auto import tqdm

from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.contextual_embeddings.corpus_runing_stats import CorpusRunningStats

try:
    from transformers.modeling_utils import PreTrainedModel
    from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
except:
    @dataclasses.dataclass
    class PreTrainedModel:
        def config_class(self) -> object:
            pass


    @dataclasses.dataclass
    class PreTrainedTokenizerFast:
        pass


class CorpusRunningStatsFactory:
    def __init__(
            self,
            corpus: Union[ParsedCorpus, OffsetCorpus],
            model: PreTrainedModel,
            tokenizer: PreTrainedTokenizerFast,
            feats_from_spacy_doc: Optional[FeatsFromSpacyDoc] = None,
            doc_segmenter: Optional[Callable[[spacy.tokens.doc.Doc], Iterable[spacy.tokens.span.Span]]] = None,
            token_normalizer: Optional[Callable[[spacy.tokens.Token], str]] = None,
            use_all_tokens_for_category_embeddings: bool = True
    ):
        """

        :param corpus:
        :param model:
        :param tokenizer:
        :param feats_from_spacy_doc: if none, use offsets
        :param doc_segmenter:
        :param token_normalizer: Function which takes spacy token and returns a string.
          Not used for embedding calculation, just feature representation. Lowercases all by default.
        :param use_all_tokens_for_category_embeddings: bool, Use all tokens in segment for category embeddings?
        """
        self.corpus = corpus
        self.model = model
        self.tokenizer = tokenizer
        self.feats_from_spacy_doc = feats_from_spacy_doc
        if not isinstance(corpus, OffsetCorpus):
            raise Exception("Since the corpus object is not an offset corpus, feats_from_spacy_doc needs to be passed.")
        self.doc_segmenter = doc_sentence_splitter if doc_segmenter is None else doc_segmenter
        self.token_normalizer = lambda x: x.lower_ if token_normalizer is None else token_normalizer
        self.use_all_tokens_for_category_embeddings = use_all_tokens_for_category_embeddings

    def build(self, verbose: bool = True) -> CorpusRunningStats:
        self.__initialize_keyword_processor()
        running_stats = self.initialize_running_stats()
        offset_df = self.__build_offset_df()

        for i, row in self.__iter_docs_and_cats(verbose=verbose):
            if isinstance(self.corpus, OffsetCorpus):
                self._add_offsets_to_running_stats(
                    doc_idx=i,
                    doc=row.Doc,
                    cat=row.Cat,
                    running_stats=running_stats,
                    offset_df=offset_df
                )
            else:
                raise Exception("Only implemented for OffsetCorpus. "
                                "ParsedCorpus implementation will happen at some point in the future.")
                # self._add_terms_to_running_stats(doc_idx=i, doc=row.Doc, cat=row.Cat, running_stats=running_stats)

        return running_stats

    def __build_offset_df(self):
        offset_data = []
        for term, values in self.corpus.get_offsets().items():
            term_idx = self.corpus.get_metadata_index(term)
            for doc_idx, offsets in values.items():
                for start, end in offsets:
                    offset_data.append([doc_idx, term_idx, start, end])
        offset_df = pd.DataFrame(offset_data, columns=['DocIdx', 'TermIdx', 'Start', 'End']).sort_values(
            by=['DocIdx', 'Start', 'End']
        ).set_index('DocIdx')
        return offset_df

    def _add_offsets_to_running_stats(self, doc_idx, doc, cat, running_stats, offset_df) -> None:
        doc_offset_df = self.__query_for_doc_offset_df(offset_df, doc_idx)
        if len(doc_offset_df):
            for segment in self.doc_segmenter(doc):
                # keywords = self.term_keyword_processor.extract_keywords(str(segment), span_info=True)
                # if keywords:

                seg_start = segment[0].idx
                seg_end = seg_start + len(str(segment))
                try:
                    annots = doc_offset_df[lambda df: (df.Start >= seg_start) & (df.End <= seg_end)]
                except:
                    print('!!!')
                    print(doc_offset_df)
                    print(seg_start, seg_end)
                    print((doc_offset_df.Start >= seg_start) & (doc_offset_df.End <= seg_end))
                    mask = (doc_offset_df.Start >= seg_start) & (doc_offset_df.End <= seg_end)
                    import pdb; pdb.set_trace()

                embeddings = None
                if len(annots):
                    embeddings, subtoken_offsets = self.__embed_segment(segment, seg_start)
                    annots.apply(
                        lambda r: self.__add_term_to_stats(
                            term=self.corpus.get_metadata_from_index(r.TermIdx),
                            kw_start=r.Start,
                            kw_end=r.End,
                            embeddings=embeddings,
                            running_stats=running_stats,
                            subtoken_offsets=subtoken_offsets,
                            cat=cat,
                            add_to_category_embeddings=not self.use_all_tokens_for_category_embeddings,
                            segment=segment,
                            seg_start=seg_start
                        ),
                        axis=1
                    )

                if self.use_all_tokens_for_category_embeddings:
                    if embeddings is None:
                        embeddings, _ = self.__embed_segment(segment, seg_start, adjust_offsets=False)
                    running_stats.add_embeddings_to_category(embeddings=embeddings, cat=cat)

    def __embed_segment(self, segment, seg_start, adjust_offsets = True):
        str_segment = str(segment)
        inputs = self.tokenizer(str_segment, return_tensors="pt", return_offsets_mapping=True)
        subtoken_offsets = inputs['offset_mapping'].cpu().detach().numpy()[0][1:-1]
        try:
            embeddings = self.__inputs_to_embeddings(inputs=inputs)
        except Exception as e:
            import pdb; pdb.set_trace()
            raise e
        if adjust_offsets:
            subtoken_offsets_whitespace_stripped = []
            for (s, e) in subtoken_offsets:
                subtoken = str_segment[s:e]
                s += len(subtoken) - len(subtoken.lstrip())
                e -= len(subtoken) - len(subtoken.rstrip())
                if s != e:
                    subtoken_offsets_whitespace_stripped.append([s, e])
            subtoken_offsets = np.array(subtoken_offsets_whitespace_stripped)
        return embeddings, subtoken_offsets.T + seg_start

    def __query_for_doc_offset_df(self, offset_df: pd.DataFrame, doc_idx: int) -> pd.DataFrame:
        try:
            doc_offset_df = offset_df.loc[doc_idx]
        except KeyError:
            return pd.DataFrame([])
        if type(doc_offset_df) == pd.Series:
            return pd.DataFrame([dict(doc_offset_df)])
        return doc_offset_df

    # def _add_terms_to_running_stats(self, doc_idx, doc, cat, running_stats) -> None:):

    def __add_term_to_stats(
            self,
            term: str,
            kw_start: int,
            kw_end: int,
            embeddings: np.array,
            running_stats: CorpusRunningStats,
            subtoken_offsets: np.array,
            cat: str,
            add_to_category_embeddings: bool,
            segment: str,
            seg_start: int
    ):
        # kw_end -= seg_start
        # kw_start -= seg_start

        subtoken_start = np.searchsorted(subtoken_offsets[0], kw_start)
        subtoken_end = np.searchsorted(subtoken_offsets[1], kw_end, side='right')
        if subtoken_start == subtoken_end:
            if subtoken_start > 0: # if the term somehow is inside another token, we just take that token's embedding
                subtoken_start -= 1
            elif subtoken_end < subtoken_offsets.shape[1] - 1: # no idea if this can happen, but to be on the safe side
                subtoken_end += 1
            else:
                print([f'|{t}|' for t in segment])
                print(kw_start, kw_end)
                print('part', str(segment)[kw_start - seg_start:kw_end - seg_start])
                print('term', term)
                print('subtoken start end', subtoken_start, subtoken_end)
                print(seg_start)
                print(subtoken_offsets)
                for s, e in subtoken_offsets.T:
                    print(s, e, str(segment)[s - seg_start:e - seg_start])
                import pdb;
                pdb.set_trace()
        kw_embedding = embeddings[subtoken_start:subtoken_end].mean(axis=0)

        if not np.isnan(kw_embedding).any():
            running_stats.add(term=term, cat=cat, embedding=kw_embedding,
                              add_to_category_embeddings=add_to_category_embeddings)

    def __inputs_to_embeddings(self, inputs):
        outputs = self.model(
            input_ids=inputs['input_ids'],
            token_type_ids=inputs['token_type_ids'],
            attention_mask=inputs['attention_mask']
        ).last_hidden_state.detach().numpy()
        embeddings = outputs[0][1:-1]
        return embeddings

    def __iter_docs_and_cats(self, verbose: bool):
        it = self.corpus.get_df()[
            [self.corpus.get_category_column(), self.corpus.get_parsed_column()]
        ].rename(
            columns={self.corpus.get_category_column(): 'Cat',
                     self.corpus.get_parsed_column(): 'Doc'}
        ).itertuples()
        if verbose:
            it = tqdm(it, total=self.corpus.get_num_docs())
        return enumerate(it)

    def initialize_running_stats(self):
        running_stats = CorpusRunningStats(
            corpus=self.corpus,
            embedding_width=None  # self.model.config_class().hidden_size
        )
        return running_stats

    def __initialize_keyword_processor(self):
        self.term_keyword_processor = flashtext.KeywordProcessor(case_sensitive=False)
        for term in self.corpus.get_terms():
            self.term_keyword_processor.add_keyword(keyword=term)

    def _get_segment_token_embeddings(self, segment: spacy.tokens.span.Span) -> np.array:
        inputs = self.tokenizer(str(segment), return_tensors="pt")
        return self.model(**inputs).last_hidden_state.detach().numpy()
