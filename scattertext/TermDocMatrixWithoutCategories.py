import collections
import re
from enum import Enum
from typing import List, Optional, Tuple, Type, Dict

import scipy.sparse
from scattertext.indexstore import IndexStoreFromList
from typing_extensions import Self
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, coo_matrix

from scattertext.CSRMatrixTools import delete_columns, CSRMatrixFactory
from scattertext.FeatureOuput import FeatureLister
from scattertext.Common import SPACY_ENTITY_TAGS, MY_ENGLISH_STOP_WORDS, DEFAULT_BACKGROUND_SCALER_ALGO, \
    DEFAULT_BACKGROUND_BETA
from scattertext.frequencyreaders.DefaultBackgroundFrequencies import DefaultBackgroundFrequencies
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring import ScaledFScore
from scattertext.indexstore.IndexStore import IndexStore
from scattertext.termranking.TermRanker import TermRanker

class MetadataReplacementRetentionPolicy(Enum):
    KEEP_ONLY_NEW = 1
    KEEP_UNMODIFIED = 2
    KEEP_ALL = 3

class TermDocMatrixWithoutCategories(object):
    def __init__(self,
                 X: csr_matrix,
                 mX: csr_matrix,
                 term_idx_store: IndexStore,
                 metadata_idx_store: IndexStore,
                 unigram_frequency_path: str=None):
        '''

        Parameters
        ----------
        X : csr_matrix
            term document matrix
        mX : csr_matrix
            metadata-document matrix
        term_idx_store : IndexStore
            Term indices
        metadata_idx_store : IndexStore
          Document metadata indices
        unigram_frequency_path : str or None
            Path to term frequency file.
        '''
        self._X = X
        self._mX = mX
        self._term_idx_store = term_idx_store
        self._metadata_idx_store = metadata_idx_store
        self._unigram_frequency_path = unigram_frequency_path
        self._background_corpus = None
        self._strict_unigram_definition = True

    def get_default_stoplist(self):
        return MY_ENGLISH_STOP_WORDS

    def allow_single_quotes_in_unigrams(self) -> Self:
        '''
        Don't filter out single quotes in unigrams
        :return: self
        '''
        self._strict_unigram_definition = False
        return self

    def compact(self, compactor, non_text: bool = False) -> Self:
        '''
        Compact term document matrix.

        Parameters
        ----------
        compactor : object
            Object that takes a Term Doc Matrix as its first argument, and has a compact function which returns a
            Term Doc Matrix like argument
        non_text : bool
            Use non text features. False by default.
        Returns
        -------
        TermDocMatrix
        '''
        return compactor.compact(self, non_text)

    def select(self, compactor, non_text: bool = False) -> Self:
        '''
        Same as compact
        '''
        return compactor.compact(self, non_text)

    def get_num_terms(self, non_text: bool = False) -> int:
        '''
        Returns
        -------
        The number of terms registered in the term doc matrix
        '''
        if non_text:
            return self.get_num_metadata()
        return len(self._term_idx_store)

    def get_num_docs(self) -> int:
        '''
        Returns
        -------
        int, number of documents
        '''
        return self._X.shape[0]

    def get_num_metadata(self) -> int:
        '''
        Returns
        -------
        int, number of unique metadata items
        '''
        return len(self.get_metadata())

    def set_background_corpus(self, background) -> Self:
        '''
        Parameters
        ----------
        background

        '''
        if issubclass(type(background), TermDocMatrixWithoutCategories):
            self._background_corpus = pd.DataFrame(background
                                                   .get_term_freq_df()
                                                   .sum(axis=1),
                                                   columns=['background']).reset_index()
            self._background_corpus.columns = ['word', 'background']
        elif (type(background) == pd.DataFrame
              and set(background.columns) == set(['word', 'background'])):
            self._background_corpus = background
        elif type(background) == pd.Series:
            self._background_corpus = background
        else:
            raise Exception('The argument named background must be a subclass of TermDocMatrix or a ' \
                            + 'DataFrame with columns "word" and "background", where "word" ' \
                            + 'is the term text, and "background" is its frequency.')

        return self

    def get_background_corpus(self):
        if self._background_corpus is not None:
            if type(self._background_corpus) == pd.DataFrame:
                return self._background_corpus['background']
            elif type(self._background_corpus) == pd.Series:
                return self._background_corpus
            return self._background_corpus
        return DefaultBackgroundFrequencies.get_background_frequency_df(self._unigram_frequency_path)

    def get_term_and_background_counts(self) -> pd.DataFrame:
        '''
        Returns
        -------
        A pd.DataFrame consisting of unigram term counts of words occurring
         in the TermDocumentMatrix and their corresponding background corpus
         counts.  The dataframe has two columns, corpus and background.

        >>> corpus.get_unigram_corpus().get_term_and_background_counts()
                          corpus  background
        obama              702.0    565739.0
        romney             570.0    695398.0
        barack             248.0    227861.0
        ...
        '''
        background_df = self._get_background_unigram_frequencies()
        if type(background_df) == pd.DataFrame:
            background_df = background_df['background']
        corpus_freq_df = self.get_term_count_df()
        corpus_unigram_freq = self._get_corpus_unigram_freq(corpus_freq_df)

        return pd.DataFrame({
            'background': background_df,
            'corpus': corpus_unigram_freq['corpus'],
        }).fillna(0)

    def get_term_count_df(self):
        return pd.DataFrame({'corpus': self._X.sum(axis=0).A1, 'term': self.get_terms()}).set_index('term')

    def _get_corpus_unigram_freq(self, corpus_freq_df: pd.DataFrame) -> pd.DataFrame:
        unigram_validator = re.compile('^[A-Za-z]+$')
        corpus_unigram_freq = corpus_freq_df.loc[[term for term
                                                  in corpus_freq_df.index
                                                  if unigram_validator.match(term) is not None]]
        return corpus_unigram_freq

    def _get_background_unigram_frequencies(self) -> pd.DataFrame:
        if self.get_background_corpus() is not None:
            return self.get_background_corpus()
        return DefaultBackgroundFrequencies.get_background_frequency_df(self._unigram_frequency_path)

    def list_extra_features(self, use_metadata: bool = True) -> List[Dict[str, str]]:
        '''
        Returns
        -------
        List of dicts.  One dict for each document, keys are metadata, values are counts
        '''
        return FeatureLister(self._get_relevant_X(use_metadata),
                             self._get_relevant_idx_store(use_metadata),
                             self.get_num_docs()).output()

    def get_terms(self, use_metadata=False) -> List[str]:
        '''
        Returns
        -------
        np.array of unique terms
        '''
        if use_metadata:
            return self.get_metadata()
        return self._term_idx_store._i2val

    def get_metadata(self) -> List[str]:
        '''
        Returns
        -------
        np.array of unique metadata
        '''
        return self._metadata_idx_store._i2val

    def get_total_unigram_count(self) -> int:
        return self._get_unigram_term_freq_df().sum()

    def _get_unigram_term_freq_df(self) -> pd.DataFrame:
        return self._get_corpus_unigram_freq(
            # self.get_term_freq_df().sum(axis=1)
            self.get_term_count_df()['corpus']
        )

    def _get_X_after_delete_terms(self,
                                  idx_to_delete_list: List[int],
                                  non_text: bool = False) -> Tuple[csr_matrix, IndexStore]:
        new_term_idx_store = self._get_relevant_idx_store(non_text).batch_delete_idx(idx_to_delete_list)
        new_X = delete_columns(self._get_relevant_X(non_text), idx_to_delete_list)
        return new_X, new_term_idx_store

    def _get_relevant_X(self, non_text: bool) -> csr_matrix:
        return self._mX if non_text else self._X

    def _get_relevant_idx_store(self, non_text: bool) -> IndexStore:
        return self._metadata_idx_store if non_text else self._term_idx_store

    def remove_infrequent_words(
            self,
            minimum_term_count: int,
            term_ranker: Type[TermRanker] = AbsoluteFrequencyRanker,
            non_text: bool = False) -> Self:
        '''
        Returns
        -------
        A new TermDocumentMatrix consisting of only terms which occur at least minimum_term_count.
        '''
        ranker = term_ranker(self)
        if non_text:
            ranker = ranker.use_non_text_features()
        tdf = ranker.get_ranks().sum(axis=1)

        return self.remove_terms(list(tdf[tdf <= minimum_term_count].index), non_text=non_text)

    def remove_word_by_document_pct(
            self,
            min_document_pct: float = 0.,
            max_document_pct: float = 1.,
            non_text: bool = False
    ) -> Self:
        '''
        Returns a copy of the corpus with terms that occur in a document percentage range.

        :param min_document_pct: float, minimum document percentage. 0 by default
        :param max_document_pct: float, maximum document percentage. 1 by default
        :param non_text: bool, use metadata?
        :return: Corpus
        '''
        tdm = self.get_term_doc_mat(non_text=non_text) > 0
        tdmpct = (tdm.sum(axis=0) / tdm.shape[0]).A1
        mask = (tdmpct >= min_document_pct) & (tdmpct <= max_document_pct)
        return self.remove_terms(np.array(self.get_terms())[mask])

    def remove_entity_tags(self) -> Self:
        '''
        Returns
        -------
        A new TermDocumentMatrix consisting of only terms in the current TermDocumentMatrix
         that aren't spaCy entity tags.

        Note: Used if entity types are censored using FeatsFromSpacyDoc(tag_types_to_censor=...).
        '''
        terms_to_remove = [term for term in self._term_idx_store._i2val
                           if any([word in SPACY_ENTITY_TAGS for word in term.split()])]
        return self.remove_terms(terms_to_remove)

    def remove_terms(self, terms: List[str],
                     ignore_absences: bool = False, non_text: bool = False) -> Self:
        '''Non-destructive term removal.

        Parameters
        ----------
        terms : list
            list of terms to remove
        ignore_absences : bool, False by default
            If term does not appear, don't raise an error, just move on.
        non_text : bool, False by default
            Remove metadata terms instead of regular terms

        Returns
        -------
        TermDocMatrix, new object with terms removed.
        '''
        idx_to_delete_list = self._build_term_index_list(ignore_absences, terms, non_text)
        return self.remove_terms_by_indices(idx_to_delete_list, non_text)

    def whitelist_terms(self, whitelist_terms: List[str], non_text: bool = False) -> Self:
        '''

        :param whitelist_terms: list[str], terms to whitelist
        :param non_text: bool, use non text featurs, default False
        :return: TermDocMatrix, new object with only terms in parameter
        '''
        return self.remove_terms(
            list(set(self.get_terms(use_metadata=non_text)) - set(whitelist_terms)),
            non_text=non_text)

    def _build_term_index_list(self,
                               ignore_absences: bool,
                               terms: List[str],
                               non_text=False) -> List[int]:
        idx_to_delete_list = []
        my_term_idx_store = self._get_relevant_idx_store(non_text)
        for term in terms:
            if term not in my_term_idx_store:
                if not ignore_absences:
                    raise KeyError('Term %s not found' % (term))
                continue
            idx_to_delete_list.append(my_term_idx_store.getidx(term))
        return idx_to_delete_list

    def _make_new_term_doc_matrix(self,
                                  new_X=None,
                                  new_mX=None,
                                  new_y=None,
                                  new_term_idx_store=None,
                                  new_category_idx_store=None,
                                  new_metadata_idx_store=None,
                                  new_y_mask=None) -> Self:
        return TermDocMatrixWithoutCategories(
            X=new_X if new_X is not None else self._X,
            mX=new_mX if new_mX is not None else self._mX,
            term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
            metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
            unigram_frequency_path=self._unigram_frequency_path
        )

    def remove_terms_used_in_less_than_num_docs(self, threshold: int, non_text: bool = False) -> Self:
        '''
        Parameters
        ----------
        threshold: int
            Minimum number of documents term should appear in to be kept
        non_text: bool
            Use non-text features instead of terms

        Returns
        -------
        TermDocMatrix, new object with terms removed.
        '''
        term_counts = self._get_relevant_X(non_text).astype(bool).astype(int).sum(axis=0).A[0]
        terms_to_remove = np.where(term_counts < threshold)[0]
        return self.remove_terms_by_indices(terms_to_remove, non_text)

    def remove_document_ids(self,
                            document_ids: List[int],
                            remove_unused_terms: bool = True,
                            remove_unused_metadata: bool = False) -> Self:
        '''

        :param document_ids: List[int], list of document ids to remove
        :return: Corpus
        '''
        y_mask = ~np.isin(np.arange(self.get_num_docs()), np.array(document_ids))
        updated_tdm = self._make_new_term_doc_matrix(
            new_X=self._X,
            new_mX=self._mX,
            new_y=None,
            new_category_idx_store=None,
            new_term_idx_store=self._term_idx_store,
            new_metadata_idx_store=self._metadata_idx_store,
            new_y_mask=y_mask
        )

        if remove_unused_terms:
            unused_term_idx = np.where(self._X[y_mask, :].sum(axis=0) == 0)[1]
            updated_tdm = updated_tdm.remove_terms_by_indices(unused_term_idx, non_text=False)

        if remove_unused_metadata:
            unused_metadata_mask = np.mask(self._mX[y_mask, :].sum(axis=0) == 0)[0]
            updated_tdm = updated_tdm.remove_terms_by_indices(unused_metadata_mask, non_text=True)

        return updated_tdm

    def remove_documents_less_than_length(self, max_length: int, non_text: bool = False) -> Self:
        '''
            `

        :param max_length: int, length of document in terms registered in corpus
        :return: Corpus
        '''
        tdm = self.get_metadata_doc_mat() if non_text else self.get_term_doc_mat()
        doc_ids_to_remove = np.where(tdm.sum(axis=1).T.A1 < max_length)
        return self.remove_document_ids(doc_ids_to_remove)

    def get_unigram_corpus(self) -> Self:
        '''
        Returns
        -------
        A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
        '''
        terms_to_ignore = self._get_non_unigrams()
        return self.remove_terms(terms_to_ignore)

    def _get_non_unigrams(self) -> List[str]:
        return [term for term
                in self._term_idx_store._i2val
                if ' ' in term or (self._strict_unigram_definition and "'" in term)]

    def get_stoplisted_unigram_corpus(self,
                                      stoplist: Optional[List[str]] = None,
                                      non_text: bool = False) -> Self:
        '''
        Parameters
        -------
        stoplist : list, optional

        Returns
        -------
        A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
        '''
        if stoplist is None:
            stoplist = self.get_default_stoplist()
        else:
            stoplist = [w.lower() for w in stoplist]
        return self._remove_terms_from_list_and_all_non_unigrams(stoplist, non_text=non_text)

    def get_stoplisted_corpus(self, stoplist=None, non_text: bool = False):
        '''
        Parameters
        -------
        stoplist : list, optional
        non_text : bool

        Returns
        -------
        A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
        '''
        if stoplist is None:
            stoplist = self.get_default_stoplist()
        return self.remove_terms([w.lower() for w in stoplist], ignore_absences=True, non_text=non_text)

    def get_stoplisted_unigram_corpus_and_custom(self, custom_stoplist, non_text: bool = False):
        '''
        Parameters
        -------
        stoplist : list of lower-cased words, optional

        Returns
        -------
        A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
        '''
        if type(custom_stoplist) == str:
            custom_stoplist = [custom_stoplist]
        return self._remove_terms_from_list_and_all_non_unigrams(
            set(self.get_default_stoplist())
            | set(w.lower() for w in custom_stoplist),
            non_text=non_text
        )

    def filter_out(self, filter_func, non_text=False):
        '''

        :param filter_func: function which takes a string and returns true or false
        :return: A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
        '''
        return self.remove_terms([x for x in self.get_terms(use_metadata=non_text) if filter_func(x)],
                                 non_text=non_text)

    def _remove_terms_from_list_and_all_non_unigrams(self, stoplist, non_text=False):
        terms_to_ignore = [term for term
                           in (self._metadata_idx_store._i2val if non_text else self._term_idx_store._i2val)
                           if ' ' in term or (self._strict_unigram_definition
                                              and ("'" in term or '’' in term))
                           or term in stoplist]
        return self.remove_terms(terms_to_ignore, non_text=non_text)

    def metadata_in_use(self) -> bool:
        '''
        Returns True if metadata values are in term doc matrix.

        Returns
        -------
        bool
        '''
        return len(self._metadata_idx_store) > 0

    def _make_all_positive_data_ones(self, new_x: csr_matrix) -> csr_matrix:
        return (new_x > 0).astype(np.int32)

    def remove_terms_by_indices(self, idx_to_delete_list: List[int], non_text: bool = False) -> Self:
        '''
        Parameters
        ----------
        idx_to_delete_list, list
        non_text, bool
            Should we remove non text features or just terms?

        Returns
        -------
        TermDocMatrix
        '''
        new_X, new_idx_store = self._get_X_after_delete_terms(idx_to_delete_list, non_text)

        return self._make_new_term_doc_matrix(new_X=self._X if non_text else new_X,
                                              new_mX=new_X if non_text else self._mX,
                                              new_y=None,
                                              new_category_idx_store=None,
                                              new_term_idx_store=self._term_idx_store if non_text else new_idx_store,
                                              new_metadata_idx_store=(new_idx_store if non_text
                                                                      else self._metadata_idx_store),
                                              new_y_mask=np.ones(new_X.shape[0]).astype(np.bool))

    def get_scaled_f_scores_vs_background(self,
                                          scaler_algo: str = DEFAULT_BACKGROUND_SCALER_ALGO,
                                          beta: float = DEFAULT_BACKGROUND_BETA) -> pd.DataFrame:
        '''
        Parameters
        ----------
        scaler_algo : str
            see get_scaled_f_scores, default 'none'
        beta : float
          default 1.
        Returns
        -------
        pd.DataFrame of scaled_f_score scores compared to background corpus
        '''
        df = self.get_term_and_background_counts()
        df['Scaled f-score'] = ScaledFScore.get_scores_for_category(
            df['corpus'], df['background'], scaler_algo, beta
        )
        return df.sort_values(by='Scaled f-score', ascending=False)

    def get_term_doc_mat(self, non_text: bool = False) -> csr_matrix:
        '''
        Returns sparse matrix representation of term-doc-matrix

        Returns
        -------
        scipy.sparse.csr_matrix
        '''
        if non_text:
            return self.get_metadata_doc_mat()
        return self._X

    def get_term_freqs(self, non_text: bool = False) -> np.array:
        return self.get_term_doc_mat(non_text=non_text).sum(axis=0).A1

    def get_term_doc_mat_coo(self, non_text: bool = False) -> coo_matrix:
        '''
        Returns sparse matrix representation of term-doc-matrix

        Returns
        -------
        scipy.sparse.coo_matrix
        '''
        return self.get_term_doc_mat(non_text=non_text).astype(np.double).tocoo()

    def get_metadata_doc_mat(self) -> csr_matrix:
        '''
        Returns sparse matrix representation of term-doc-matrix

        Returns
        -------
        scipy.sparse.csr_matrix
        '''
        return self._mX

    def term_doc_lists(self) -> Dict:
        '''
        Returns
        -------
        dict
        '''
        doc_ids = self._X.transpose().tolil().rows
        terms = self._term_idx_store.values()
        return dict(zip(terms, doc_ids))

    def apply_ranker(self,
                     term_ranker: Type[TermRanker],
                     use_non_text_features: bool,
                     label_append: str = ' freq') -> pd.DataFrame:
        '''
        Parameters
        ----------
        term_ranker : TermRanker

        Returns
        -------
        pd.Dataframe
        '''
        if use_non_text_features:
            return term_ranker(self).use_non_text_features().get_ranks(label_append=label_append)
        return term_ranker(self).get_ranks(label_append=label_append)

    def add_doc_names_as_metadata(self, doc_names: List[str]) -> Self:
        '''
        :param doc_names: array-like[str], document names of reach document
        :return: Corpus-like object with doc names as metadata. If two documents share the same name
        (doc number) will be appended to their names.
        '''
        if len(doc_names) != self.get_num_docs():
            raise Exception("The parameter doc_names contains %s elements. "
                            "It should have %s elements, one per document." % (len(doc_names), self.get_num_docs()))

        doc_names_counter = collections.Counter(np.array(doc_names))
        metafact = CSRMatrixFactory()
        metaidxstore = IndexStore()
        doc_id_uses = collections.Counter()
        for i in range(self.get_num_docs()):
            doc_id = doc_names[i]
            if doc_names_counter[doc_id] > 1:
                doc_id_uses[doc_id] += 1
                doc_name_idx = metaidxstore.getidx('%s (%s)' % (doc_id, doc_id_uses[doc_id]))
            else:
                doc_name_idx = metaidxstore.getidx(doc_id)
            metafact[i, i] = doc_name_idx
        return self.add_metadata(metafact.get_csr_matrix(), metaidxstore)

    def get_term_index(self, term: str) -> int:
        return self._term_idx_store.getidxstrict(term)

    def get_metadata_index(self, term: str) -> int:
        return self._metadata_idx_store.getidxstrict(term)

    def get_metadata_from_index(self, index: int) -> str:
        return self._metadata_idx_store.getval(index)

    def get_term_from_index(self, index: int) -> str:
        return self._term_idx_store.getval(index)

    def get_term_index_store(self, non_text=False) -> IndexStore:
        return self._metadata_idx_store if non_text else self._term_idx_store

    def get_document_ids_with_terms(self, terms: List[str], use_non_text_features: bool = False) -> np.array:
        return np.where(
            self._get_relevant_X(use_non_text_features)[
            :,
            [self._term_idx_store.getidx(x) for x in terms if x in self._term_idx_store]
            ].sum(axis=1).A1 > 0
        )[0]

    def add_metadata(self, metadata_matrix: csr_matrix, meta_index_store: IndexStore) -> Self:
        '''
        Returns a new corpus with the metadata matrix and index store integrated.

        :param metadata_matrix: scipy.sparse matrix (# docs, # metadata)
        :param meta_index_store: IndexStore of metadata values
        :return: TermDocMatrixWithoutCategories
        '''
        assert isinstance(meta_index_store, IndexStore)
        assert len(metadata_matrix.shape) == 2
        assert metadata_matrix.shape[0] == self.get_num_docs()
        return self._make_new_term_doc_matrix(new_X=self._X,
                                              new_y=None,
                                              new_category_idx_store=None,
                                              new_y_mask=np.ones(self.get_num_docs()).astype(bool),
                                              new_mX=metadata_matrix,
                                              new_term_idx_store=self._term_idx_store,
                                              new_metadata_idx_store=meta_index_store)

    def rename_metadata(
            self,
            old_to_new_vals: List[Tuple[str, str]],
            policy: MetadataReplacementRetentionPolicy = MetadataReplacementRetentionPolicy.KEEP_ONLY_NEW
    ) -> Self:
        new_mX, new_metadata_idx_store = self._remap_metadata(old_to_new_vals, policy)
        return self._make_new_term_doc_matrix(
            new_X=self._X,
            new_mX=new_mX,
            new_term_idx_store=self._term_idx_store,
            new_metadata_idx_store=new_metadata_idx_store)

    def _remap_metadata(self,
                        old_to_new_vals: List[Tuple[str, str]],
                        policy: MetadataReplacementRetentionPolicy) -> Tuple[csr_matrix, IndexStore]:
        old_to_new_df = self._get_old_to_new_metadata_mapping_df(old_to_new_vals)

        keep_vals = self._get_metadata_mapped_values_to_keep(old_to_new_df)
        new_val_mX = np.zeros(shape=(self._mX.shape[0], old_to_new_df.New.nunique()))
        if policy.value == MetadataReplacementRetentionPolicy.KEEP_UNMODIFIED.value:
            new_metadata_idx_store = IndexStoreFromList.build(keep_vals)
        elif policy.value == MetadataReplacementRetentionPolicy.KEEP_ONLY_NEW.value:
            new_metadata_idx_store = IndexStore()
        else:
            raise Exception(f"Policy {policy} not supporteds")

        for new_val_i, (new_name, new_df) in enumerate(old_to_new_df.groupby('New')):
            new_metadata_idx_store.getidx(new_name)
            new_val_counts = self._mX[:, self._metadata_idx_store.getidxstrictbatch(new_df.Old.values)]
            new_val_mX[:, new_val_i] = new_val_counts.sum(axis=1).T[0]

        if policy.value == MetadataReplacementRetentionPolicy.KEEP_UNMODIFIED.value:
            keep_mX = self._mX[:, self._metadata_idx_store.getidxstrictbatch(keep_vals)]
            new_mX = scipy.sparse.hstack([keep_mX, new_val_mX], format='csr', dtype=self._mX.dtype)
        else: #elif policy.value == MetadataReplacementRetentionPolicy.KEEP_ONLY_NEW.value:
            new_mX = scipy.sparse.csr_matrix(new_val_mX, dtype=self._mX.dtype)

        return new_mX, new_metadata_idx_store

    def _get_metadata_mapped_values_to_keep(self, old_to_new_df: pd.DataFrame) -> List[str]:
        keep_vals = [x for x in self.get_metadata()
                     if x not in set(old_to_new_df.Old.unique()) | set(old_to_new_df.New.unique())]
        return keep_vals

    def _get_old_to_new_metadata_mapping_df(self, old_to_new_vals: List[Tuple[str, str]]) -> pd.DataFrame:
        old_to_new_vals = [(old, new) for old, new in old_to_new_vals
                           if old in self._metadata_idx_store]
        return pd.DataFrame(old_to_new_vals, columns=['Old', 'New'])
