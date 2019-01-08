from abc import ABCMeta, abstractmethod

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import vstack

from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termranking.TermRanker import TermRanker

try:
    from future.utils import with_metaclass
except:
    from six import with_metaclass


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
    def __init__(self, corpus, *args, **kwargs):
        self.corpus_ = corpus
        self.category_ids_ = corpus._y
        self.tdf_ = None
        self._set_scorer_args(**kwargs)
        self.term_ranker_ = AbsoluteFrequencyRanker(corpus)
        self.use_metadata_ = False
        self.category_name_is_set_ = False

    @abstractmethod
    def _set_scorer_args(self, **kwargs):
        pass

    def use_metadata(self):
        self.use_metadata_ = True
        self.term_ranker_.use_non_text_features()
        return self

    def set_term_ranker(self, term_ranker):
        assert issubclass(term_ranker, TermRanker)
        self.term_ranker_ = term_ranker(self.corpus_)
        if self.use_metadata_:
            self.term_ranker_.use_non_text_features()
        return self

    def is_category_name_set(self):
        return self.category_name_is_set_

    def set_categories(self,
                       category_name,
                       not_category_names=[],
                       neutral_category_names=[]):
        '''
        Specify the category to score. Optionally, score against a specific set of categories.
        '''
        tdf = self.term_ranker_.get_ranks()
        d = {'cat': tdf[category_name + ' freq']}
        if not_category_names == []:
            not_category_names = [c + ' freq' for c in self.corpus_.get_categories()
                                  if c != category_name]
        else:
            not_category_names = [c + ' freq' for c in not_category_names]
        d['ncat'] = tdf[not_category_names].sum(axis=1)
        if neutral_category_names == []:
            # neutral_category_names = [c + ' freq' for c in self.corpus.get_categories()
            #                          if c != category_name and c not in not_category_names]
            pass
        else:
            neutral_category_names = [c + ' freq' for c in neutral_category_names]
        for i, c in enumerate(neutral_category_names):
            d['neut%s' % (i)] = tdf[c]
        self.tdf_ = pd.DataFrame(d)
        self.category_name = category_name
        self.not_category_names = [c[:-5] for c in not_category_names]
        self.neutral_category_names = [c[:-5] for c in neutral_category_names]
        self.category_name_is_set_ = True
        return self

    def _get_X(self):
        return self.corpus_.get_metadata_doc_mat() if self.use_metadata_ else self.term_ranker_.get_X()

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
        cat_X = X[np.isin(self.corpus_.get_category_names_by_row(),
                          [self.category_name] + self.neutral_category_names), :]
        ncat_X = X[np.isin(self.corpus_.get_category_names_by_row(),
                           self.not_category_names + self.neutral_category_names), :]
        if len(self.neutral_category_names) > 0:
            neut_X = [np.isin(self.corpus_.get_category_names_by_row(), self.neutral_category_names)]
            cat_X = vstack([cat_X, neut_X])
            ncat_X = vstack([ncat_X, neut_X])
        return cat_X, ncat_X

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
