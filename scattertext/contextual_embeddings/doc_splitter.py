from typing import Iterable, Callable

import numpy as np
import pandas as pd
import spacy


def doc_sentence_splitter(doc: spacy.tokens.doc.Doc) -> Iterable[spacy.tokens.span.Span]:
    for sent in doc.sents:
        non_blank = [t.i for t in sent if t.orth_.strip() != '']
        if len(non_blank):
            yield doc[non_blank[0]:non_blank[-1] + 1]


class SubwordSensitiveSentenceBoundedSplitter:
    def __init__(
            self,
            tokenizer: Callable,
            max_segment_size: int = 100,
    ):
        self.tokenizer = tokenizer
        self.max_segment_size = max_segment_size

    def segment(self, doc: spacy.tokens.doc.Doc) -> Iterable[spacy.tokens.span.Span]:
        sent_interval_index = pd.IntervalIndex.from_tuples(
            [(s[0].idx, s[0].idx + len(str(s))) for s in doc.sents])

        subtokens = self.tokenizer(str(doc), return_offsets_mapping=True)

        subtoken_offset_df = pd.DataFrame(
            subtokens['offset_mapping'],
            columns=['SubStart', 'SubEnd'],
        ).assign(
            InputId=subtokens['input_ids'],
            StartSentenceId=lambda df: sent_interval_index.get_indexer(df.SubStart),
            EndSentenceId=lambda df: sent_interval_index.get_indexer(df.SubEnd),
            SentenceId=lambda df: np.where((df.StartSentenceId > 0) & (df.EndSentenceId > 0),
                                           (df.EndSentenceId + df.StartSentenceId) / 2,
                                           df[['StartSentenceId', 'EndSentenceId']].max(axis=1)),

        )[
            lambda df: (df.SubStart < df.SubEnd) & (df.SentenceId > -1)
        ].assign(
            Count=lambda df: np.arange(len(df)) + 1,
        )

        subtoken_subsent_offset_df = pd.merge(
            subtoken_offset_df,
            pd.DataFrame({'SentStart': subtoken_offset_df.groupby('SentenceId').Count.min()}),
            left_on='SentenceId',
            right_index=True
        ).assign(
            SentCount=lambda df: df.Count - df.SentStart,
            SubsentenceId=lambda df: df.SentCount // self.max_segment_size
        )

        def limit_cum_sum_slow(x):
            if limit_cum_sum.prev + x > self.max_segment_size:
                limit_cum_sum.prev = x
                limit_cum_sum.segment_num += 1
                return limit_cum_sum.segment_num
            limit_cum_sum.prev += x
            return limit_cum_sum.segment_num

        limit_cum_sum = np.vectorize(limit_cum_sum_slow, otypes=[np.int32])
        limit_cum_sum.prev = 0
        limit_cum_sum.segment_num = 0

        for _, segment_df in subtoken_subsent_offset_df.groupby(
                ['SentenceId', 'SubsentenceId']
        ).apply(lambda gdf: pd.Series({
            'Length': len(gdf),
            'Start': gdf.SubStart.min(),
            'End': gdf.SubEnd.max(),
        })).assign(
            Supersegment=lambda df: limit_cum_sum(df.Length.values)
        ).reset_index().groupby('Supersegment'):
            if segment_df.Length.sum() > self.max_segment_size:
                import pdb; pdb.set_trace()
            yield doc.char_span(segment_df.Start.min(), segment_df.End.max(), alignment_mode='expand')

    def __segments_from_subtoken_offsets(self, subtoken_offset_df: pd.DataFrame) -> pd.DataFrame:
        return subtoken_offset_df[
            lambda df: df.SentenceId == df.SentenceId.apply(int)
        ].groupby('SentenceId').apply(lambda gdf: pd.Series({
            'Length': len(gdf),
            'Start': gdf.SubStart.min(),
            'End': gdf.SubEnd.max(),
            'InputId': gdf.InputId.values
        })).reset_index().assign(
            Segment=lambda df: self.__sentence_segments_from_subtokens(df)
        ).groupby('Segment').agg({
            'Start': 'min',
            'End': 'max',
            'SentenceId': lambda x: list(int(x) for x in sorted(x)),
            'InputId': np.hstack
        })

    def __sentence_segments_from_subtokens(self, sentence_df: pd.DataFrame) -> pd.DataFrame:
        inside_segment = False
        current_segment = 0
        tokens_in_segment = 0
        sentence_segments = []

        for sentence_id, row in sentence_df.iterrows():
            if inside_segment:
                tokens_in_segment += row.Length
            if int(sentence_id) == sentence_id:
                if inside_segment is False:
                    inside_segment = True
                potential_additional_tokens = 0
                if sentence_id + 0.5 in sentence_df.index:
                    potential_additional_tokens += sentence_df.loc[sentence_id + 0.5].Length
                if sentence_id + 1 in sentence_df.index:
                    potential_additional_tokens += sentence_df.loc[sentence_id + 1].Length
                sentence_segments.append(current_segment)
                if tokens_in_segment + potential_additional_tokens <= self.max_segment_size:
                    tokens_in_segment += potential_additional_tokens
                else:
                    tokens_in_segment = potential_additional_tokens
                    current_segment += 1
                    inside_segment = False
            else:
                sentence_segments.append(current_segment if inside_segment else -1)
        return pd.DataFrame(sentence_segments)
