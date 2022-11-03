import pandas as pd
import numpy as np
from scipy.stats import norm

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer

BNS_ALPHA_DEFAULT = 0.005 # Note: I've found this works better for content analysis than 0.0005 as suggested by Forman

# Reference: George Forman. 2008. BNS feature scaling: an improved representation over tf-idf for
# svm text classification. In Proceedings of the 17th ACM conference on Information and
# knowledge management (CIKM '08). Association for Computing Machinery, New York, NY, USA,
# 263–270. https://doi.org/10.1145/1458082.1458119

class BNSScorer(CorpusBasedTermScorer):
    def _set_scorer_args(self, **kwargs):
        self.alpha = kwargs.get('alpha', BNS_ALPHA_DEFAULT)
        assert 0 <= self.alpha <= 1

    def get_score_df(self):
        data = {}
        X = self._get_X() > 0
        y = self.corpus_._y
        for cat_i, cat in enumerate(self.corpus_.get_categories()):
            n_cat_is = [x for x in range(len(self.corpus_.get_categories())) if x != cat_i]
            bns_scores = self._get_bns_score_for_category_index(cat_i, n_cat_is, X, y)
            data[cat] = bns_scores
        return pd.DataFrame(data, index=self._get_index())

    def _get_bns_score_for_category_index(self, cat_i, not_cat_is, X, y):
        cat_mask = y == cat_i
        not_cat_mask = np.logical_or.reduce([y == i for i in not_cat_is])
        invn_tpr = self._invnorm(X[cat_mask].sum(axis=0).A1/np.sum(cat_mask))
        invn_fpr = self._invnorm(X[not_cat_mask].sum(axis=0).A1/np.sum(not_cat_mask))
        return invn_tpr - invn_fpr

    def _invnorm(self, scores: np.array) -> np.array:
        scores[scores < self.alpha] = self.alpha
        scores[scores > 1 - self.alpha] = 1 - self.alpha
        return norm.ppf(scores)

    def get_scores(self, *args) -> pd.Series:
        return pd.Series(
            self._get_bns_score_for_category_index(
                cat_i=self.corpus_.get_categories().index(self.category_name),
                not_cat_is=[self.corpus_.get_categories().index(c) for c in self.not_category_names],
                X=self._get_X() > 0,
                y=self.corpus_._y
            ),
            index=self._get_index()
        )

    def get_name(self):
        return f"Bi-normal separation (alpha={self.alpha})"
