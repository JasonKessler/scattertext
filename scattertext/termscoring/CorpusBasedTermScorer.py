from abc import ABCMeta, abstractmethod
from typing import Tuple, TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import vstack

from scattertext.util import inherits_from
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termranking.TermRanker import TermRanker

try:
    from future.utils import with_metaclass
except:
    from six import with_metaclass

if TYPE_CHECKING:
    from scattertext.ParsedCorpus import ParsedCorpus


def sparse_var(X):
    '''
    Compute variance from
    :param X:
    :return:
    '''
    Xc = X.copy()
    Xc.data **= 2
    return np.array(Xc.mean(axis=0) - np.power(X.mean(axis=0), 2))[0]


class NeedToSetCategoriesException(Exception):
    pass


class CorpusBasedTermScorer(with_metaclass(ABCMeta, object)):
    def __init__(self, corpus: "ParsedCorpus", *args, **kwargs):
        self.corpus_ = corpus
        self.category_ids_ = corpus._y
        self.tdf_ = None
        self.use_metadata_ = kwargs.get('non_text', False) \
                             or kwargs.get('use_metadata', False) \
                             or kwargs.get('use_non_text_features', False)
        self.category_name_is_set_ = False
        self._doc_sizes = None
        self._set_scorer_args(**kwargs)
        self.term_ranker_ = self._get_default_ranker(corpus)

    def _get_default_ranker(self, corpus):
        return AbsoluteFrequencyRanker(corpus).set_non_text(non_text=self.use_metadata_)

    @abstractmethod
    def _set_scorer_args(self, **kwargs):
        pass

    def set_doc_sizes(self, doc_sizes: np.array) -> 'CorpusBasedTermScorer':
        assert len(doc_sizes) == self.corpus_.get_num_docs()
        self._doc_sizes = doc_sizes
        return self

    def use_token_counts_as_doc_sizes(self) -> 'CorpusBasedTermScorer':
        return self.set_doc_sizes(doc_sizes=self.corpus_.get_parsed_docs().apply(len).values)

    def get_doc_sizes(self) -> np.array:
        if self._doc_sizes is None:
            return self._get_X().sum(axis=1)
        return self._doc_sizes

    def _get_cat_size(self) -> float:
        return self.get_doc_sizes()[self._get_cat_x_row_mask()].sum()

    def _get_ncat_size(self) -> float:
        return self.get_doc_sizes()[self._get_ncat_x_row_mask()].sum()

    def use_metadata(self) -> 'CorpusBasedTermScorer':
        self.use_metadata_ = True
        self.term_ranker_ = self.term_ranker_.use_non_text_features()
        return self

    def set_term_ranker(self, term_ranker) -> 'CorpusBasedTermScorer':
        if inherits_from(term_ranker, 'TermRanker'):
            self.term_ranker_ = term_ranker(self.corpus_)
        else:
            self.term_ranker_ = term_ranker
        # print('trerm ranker type', type(self.term_ranker_)
        # assert inherits_from(self.term_ranker_, TermRanker)
        if self.use_metadata_:
            self.term_ranker_.use_non_text_features()
        return self

    def get_term_ranker(self) -> TermRanker:
        return self.term_ranker_

    def is_category_name_set(self):
        return self.category_name_is_set_

    def set_categories(self,
                       category_name,
                       not_category_names=[],
                       neutral_category_names=[]):
        '''
        Specify the category to score. Optionally, score against a specific set of categories.
        '''

        tdf = self.term_ranker_.set_non_text(non_text=self.use_metadata_).get_ranks(label_append='')
        d = {'cat': tdf[str(category_name)]}
        if not_category_names == []:
            not_category_names = [str(c) for c in self.corpus_.get_categories()
                                  if c != category_name]
        else:
            not_category_names = [str(c) for c in not_category_names]
        d['ncat'] = tdf[not_category_names].sum(axis=1)
        if neutral_category_names == []:
            # neutral_category_names = [c for c in self.corpus.get_categories()
            #                          if c != category_name and c not in not_category_names]
            pass
        else:
            neutral_category_names = [str(c) for c in neutral_category_names]
        for i, c in enumerate(neutral_category_names):
            d['neut%s' % (i)] = tdf[c]
        self.tdf_ = pd.DataFrame(d)
        self.category_name = category_name
        self.not_category_names = [c for c in not_category_names]
        self.neutral_category_names = [c for c in neutral_category_names]
        self.category_name_is_set_ = True
        return self

    def _get_X(self):
        # return self.corpus_.get_metadata_doc_mat() if self.use_metadata_ else self.term_ranker_.get_term_doc_mat()
        return self.term_ranker_.get_term_doc_mat()

    def get_t_statistics(self):
        '''
        In this case, parameters a and b aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------

        '''

        X = self._get_X()
        cat_X, ncat_X = self._get_cat_and_ncat(X)

        mean_delta = self._get_mean_delta(cat_X, ncat_X)
        cat_var = sparse_var(cat_X)
        ncat_var = sparse_var(ncat_X)
        cat_n = cat_X.shape[0]
        ncat_n = ncat_X.shape[0]
        pooled_stderr = np.sqrt(cat_var / cat_n + ncat_var / ncat_n)

        tt = mean_delta / pooled_stderr

        # Use Satterthaite-Welch adjustment for degrees of freedom
        degs_of_freedom = (cat_var ** 2 / cat_n + ncat_var ** 2 / ncat_n) ** 2 / (
                (cat_var ** 2 / cat_n) ** 2 / (cat_n - 1)
                + (ncat_var ** 2 / ncat_n) ** 2 / (ncat_n - 1)
        )

        only_in_neutral_mask = self.tdf_[['cat', 'ncat']].sum(axis=1) == 0
        pvals = stats.t.sf(np.abs(tt), degs_of_freedom)
        tt[only_in_neutral_mask] = 0
        pvals[only_in_neutral_mask] = 0

        return tt, pvals

    def _get_mean_delta(self, cat_X, ncat_X):
        return np.array(cat_X.mean(axis=0) - ncat_X.mean(axis=0))[0]

    def _get_cat_and_ncat(self, X):
        if self.category_name_is_set_ is False:
            raise NeedToSetCategoriesException()
        cat_X = X[self._get_cat_x_row_mask(), :]
        ncat_X = X[self._get_ncat_x_row_mask(), :]
        if self.neutral_category_names:
            neut_X = X[self._get_neut_row_mask(), :]
            cat_X = vstack([cat_X, neut_X])
            ncat_X = vstack([ncat_X, neut_X])
        return cat_X, ncat_X

    def _get_neut_row_mask(self):
        return np.isin(self.corpus_.get_category_names_by_row(), self.neutral_category_names)

    def _get_ncat_x_row_mask(self):
        return np.isin(self.corpus_.get_category_names_by_row(), self.not_category_names)

    def _get_cat_x_row_mask(self):
        return np.isin(self.corpus_.get_category_names_by_row(), [self.category_name])

    def _get_index(self):
        return self.corpus_.get_metadata() if self.use_metadata_ else self.corpus_.get_terms()

    @abstractmethod
    def get_scores(self, *args):
        '''
        Args are ignored

        Returns
        -------
        '''

    @abstractmethod
    def get_name(self):
        pass

    def _get_terms(self):
        return self.corpus_.get_terms(use_metadata=self.use_metadata_)

    def _get_num_terms(self):
        return self.corpus_.get_num_terms(non_text=self.use_metadata_)

    def get_score_df(self, label_append=''):
        return self.get_term_ranker().get_ranks(label_append=label_append).assign(
            Metric=self.get_scores()
        ).sort_values(
            by='Metric', ascending=True
        ).rename(columns={
            'Metric': self.get_name()
        })

    def __get_f1_f2_from_args(self, args) -> Tuple[np.array, np.array]:
        f1, f2 = args
        assert len(f1) == len(f2)
        assert len(f1) == len(self._get_terms())
        return f1, f2
