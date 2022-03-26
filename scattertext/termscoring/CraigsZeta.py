import numpy as np
import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class CraigsZeta(CorpusBasedTermScorer):
    """
    Zeta function from:

    Pervez Rizvi. The interpretation of Zeta test results.
    Digital Scholarship in the Humanities, Volume 34, Issue 2, June 2019, Pages 401–418,

    The score assumes that each document ("segment" in this literature) is approximately of equal size.
    Rizvi reports segment sizes being 900-6,000 words.

    Z_t = (# segments with type t labeled in the target category)/(# segments in target category) -
     (# segments with type t labeled not in the target category)/(# segments not in target category)

    """

    def _set_scorer_args(self, **kwargs):
        self.constant = kwargs.get('constant', 0.01)

    def get_scores(self, *args):
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        X = self._get_X() > 0
        cat_X, ncat_X = self._get_cat_and_ncat(X)
        return self._get_zeta_score(cat_X, ncat_X)

    def get_score_df(self, *args):
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        X = self._get_X() > 0
        cat_X, ncat_X = self._get_cat_and_ncat(X)
        score = self._get_zeta_score(cat_X, ncat_X)
        return pd.DataFrame({
            'Term': self.corpus_.get_terms(),
            'Base': cat_X.sum(axis=0).A1,
            'Counter': ncat_X.sum(axis=0).A1,
            'Score': score
        }).set_index('Term')

    def _get_zeta_score(self, cat_X, ncat_X):
        return (
                (cat_X.sum(axis=0) + self.constant) / (cat_X.shape[0] + self.constant)
                - (ncat_X.sum(axis=0) + self.constant) / (ncat_X.shape[0] + self.constant)
        ).A1

    def get_name(self):
        return 'Craigs Zeta'

class ChiSquareZeta(CraigsZeta):
    def _get_zeta_score(self, cat_X, ncat_X):
        return (
                (cat_X.sum(axis=0) + self.constant) / (cat_X.shape[0] + self.constant)
                - (ncat_X.sum(axis=0) + self.constant) / (ncat_X.shape[0] + self.constant)
        ).A1