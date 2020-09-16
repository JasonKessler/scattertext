import collections
import re

import numpy as np
import pandas as pd

from scattertext.CSRMatrixTools import delete_columns, CSRMatrixFactory
from scattertext.FeatureOuput import FeatureLister
from scattertext.Common import SPACY_ENTITY_TAGS, MY_ENGLISH_STOP_WORDS, DEFAULT_BACKGROUND_SCALER_ALGO, \
    DEFAULT_BACKGROUND_BETA
from scattertext.frequencyreaders.DefaultBackgroundFrequencies import DefaultBackgroundFrequencies
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring import ScaledFScore
from scattertext.indexstore.IndexStore import IndexStore


class TermDocMatrixWithoutCategories(object):
    def __init__(self, X, mX, term_idx_store, metadata_idx_store, unigram_frequency_path=None):
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

    def allow_single_quotes_in_unigrams(self):
        '''
        Don't filter out single quotes in unigrams
        :return: self
        '''
        self._strict_unigram_definition = False
        return self


    def compact(self, compactor, non_text=False):
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

    def select(self, compactor, non_text=False):
        '''
        Same as compact
        '''
        return compactor.compact(self, non_text)

    def get_num_terms(self):
        '''
        Returns
        -------
        The number of terms registered in the term doc matrix
        '''
        return len(self._term_idx_store)

    def get_num_docs(self):
        '''
        Returns
        -------
        int, number of documents
        '''
        return self._X.shape[0]

    def get_num_metadata(self):
        '''
        Returns
        -------
        int, number of unique metadata items
        '''
        return len(self.get_metadata())

    def set_background_corpus(self, background):
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
        else:
            raise Exception('The argument named background must be a subclass of TermDocMatrix or a ' \
                            + 'DataFrame with columns "word" and "background", where "word" ' \
                            + 'is the term text, and "background" is its frequency.')

    def get_background_corpus(self):
        if self._background_corpus is not None:
            return self._background_corpus
        return DefaultBackgroundFrequencies.get_background_frequency_df(self._unigram_frequency_path)

    def get_term_and_background_counts(self):
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
        corpus_freq_df = self.get_term_count_df()
        corpus_unigram_freq = self._get_corpus_unigram_freq(corpus_freq_df)
        df = corpus_unigram_freq.join(background_df, how='outer').fillna(0)
        return df

    def get_term_count_df(self):
        return pd.DataFrame({'corpus': self._X.sum(axis=0).A1, 'term': self.get_terms()}).set_index('term')

    def _get_corpus_unigram_freq(self, corpus_freq_df):
        unigram_validator = re.compile('^[A-Za-z]+$')
        corpus_unigram_freq = corpus_freq_df.loc[[term for term
                                                 in corpus_freq_df.index
                                                 if unigram_validator.match(term) is not None]]
        return corpus_unigram_freq

    def _get_background_unigram_frequencies(self):
        if self.get_background_corpus() is not None:
            return self.get_background_corpus()
        return DefaultBackgroundFrequencies.get_background_frequency_df(self._unigram_frequency_path)

    def list_extra_features(self):
        '''
        Returns
        -------
        List of dicts.  One dict for each document, keys are metadata, values are counts
        '''
        return FeatureLister(self._mX,
                             self._metadata_idx_store,
                             self.get_num_docs()).output()

    def get_terms(self):
        '''
        Returns
        -------
        np.array of unique terms
        '''
        return self._term_idx_store._i2val

    def get_metadata(self):
        '''
        Returns
        -------
        np.array of unique metadata
        '''
        return self._metadata_idx_store._i2val

    def get_total_unigram_count(self):
        return self._get_unigram_term_freq_df().sum()

    def _get_unigram_term_freq_df(self):
        return self._get_corpus_unigram_freq(
            # self.get_term_freq_df().sum(axis=1)
            self.get_term_count_df()['corpus']
        )

    def _get_X_after_delete_terms(self, idx_to_delete_list, non_text=False):
        new_term_idx_store = self._get_relevant_idx_store(non_text).batch_delete_idx(idx_to_delete_list)
        new_X = delete_columns(self._get_relevant_X(non_text), idx_to_delete_list)
        return new_X, new_term_idx_store

    def _get_relevant_X(self, non_text):
        return self._mX if non_text else self._X

    def _get_relevant_idx_store(self, non_text):
        return self._metadata_idx_store if non_text else self._term_idx_store

    def remove_infrequent_words(self, minimum_term_count, term_ranker=AbsoluteFrequencyRanker):
        '''
        Returns
        -------
        A new TermDocumentMatrix consisting of only terms which occur at least minimum_term_count.
        '''
        tdf = term_ranker(self).get_ranks().sum(axis=1)
        return self.remove_terms(list(tdf[tdf <= minimum_term_count].index))

    def remove_entity_tags(self):
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

    def remove_terms(self, terms, ignore_absences=False, non_text=False):
        '''Non destructive term removal.

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


    def whitelist_terms(self, whitelist_terms):
        '''

        :param whitelist_terms: list[str], terms to whitelist
        :return: TermDocMatrix, new object with only terms in parameter
        '''
        return self.remove_terms(list(set(self.get_terms()) - set(whitelist_terms)))

    def _build_term_index_list(self, ignore_absences, terms, non_text=False):
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
                                  new_y_mask=None):
        return TermDocMatrixWithoutCategories(
            X=new_X if new_X is not None else self._X,
            mX=new_mX if new_mX is not None else self._mX,
            term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
            metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
            unigram_frequency_path=self._unigram_frequency_path
        )

    def remove_terms_used_in_less_than_num_docs(self, threshold, non_text=False):
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

    def get_unigram_corpus(self):
        '''
        Returns
        -------
        A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
        '''
        terms_to_ignore = self._get_non_unigrams()
        return self.remove_terms(terms_to_ignore)

    def _get_non_unigrams(self):
        return [term for term
                in self._term_idx_store._i2val
                if ' ' in term or (self._strict_unigram_definition and "'" in term)
        ]

    def get_stoplisted_unigram_corpus(self, stoplist=None):
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
        return self._remove_terms_from_list(stoplist)

    def get_stoplisted_unigram_corpus_and_custom(self,
                                                 custom_stoplist):
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
        return self._remove_terms_from_list(set(self.get_default_stoplist())
                                            | set(w.lower() for w in custom_stoplist))

    def _remove_terms_from_list(self, stoplist):
        terms_to_ignore = [term for term
                           in self._term_idx_store._i2val
                           if ' ' in term or (self._strict_unigram_definition
                                              and ("'" in term or '’' in term))
                           or term in stoplist]
        return self.remove_terms(terms_to_ignore)

    def metadata_in_use(self):
        '''
        Returns True if metadata values are in term doc matrix.

        Returns
        -------
        bool
        '''
        return len(self._metadata_idx_store) > 0

    def _make_all_positive_data_ones(self, newX):
        # type: (sparse_matrix) -> sparse_matrix
        return (newX > 0).astype(np.int32)

    def get_doc_lengths(self):
        '''
        Returns a list of document lengths in words

        Returns
        -------
        np.array
        '''
        idx_to_delete_list = self._build_term_index_list(True, self._get_non_unigrams())
        unigram_X, _ = self._get_X_after_delete_terms(idx_to_delete_list)
        return unigram_X.sum(axis=1).A1

    def remove_terms_by_indices(self, idx_to_delete_list, non_text=False):
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
                                          scaler_algo=DEFAULT_BACKGROUND_SCALER_ALGO,
                                          beta=DEFAULT_BACKGROUND_BETA):
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

    def get_term_doc_mat(self):
        '''
        Returns sparse matrix representation of term-doc-matrix

        Returns
        -------
        scipy.sparse.csr_matrix
        '''
        return self._X

    def get_term_doc_mat_coo(self):
        '''
        Returns sparse matrix representation of term-doc-matrix

        Returns
        -------
        scipy.sparse.coo_matrix
        '''
        return self._X.astype(np.double).tocoo()


    def get_metadata_doc_mat(self):
        '''
        Returns sparse matrix representation of term-doc-matrix

        Returns
        -------
        scipy.sparse.csr_matrix
        '''
        return self._mX

    def term_doc_lists(self):
        '''
        Returns
        -------
        dict
        '''
        doc_ids = self._X.transpose().tolil().rows
        terms = self._term_idx_store.values()
        return dict(zip(terms, doc_ids))

    def apply_ranker(self, term_ranker, use_non_text_features):
        '''
        Parameters
        ----------
        term_ranker : TermRanker

        Returns
        -------
        pd.Dataframe
        '''
        if use_non_text_features:
            return term_ranker(self).use_non_text_features().get_ranks()
        return term_ranker(self).get_ranks()

    def add_doc_names_as_metadata(self, doc_names):
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

    def add_metadata(self, metadata_matrix, meta_index_store):
        '''
        Returns a new corpus with a the metadata matrix and index store integrated.

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
