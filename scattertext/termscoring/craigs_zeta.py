import pandas as pd
import numpy as np
from scattertext.termranking import OncePerDocFrequencyRanker

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer

class CraigsZetaScorer(CorpusBasedTermScorer):
    """
    Zeta function from:

    Pervez Rizvi. The interpretation of Zeta test results.
    Digital Scholarship in the Humanities, Volume 34, Issue 2, June 2019, Pages 401–418,

    The score assumes that each document ("segment" in this literature) is approximately of equal size.
    Rizvi reports segment sizes being 900-6,000 words.

    Z_t = (# segments with type t labeled in the target category)/(# segments in target category) +
     (# segments with type t labeled not in the target category)/(# segments not in target category)

    """

    def _set_scorer_args(self, **kwargs):
        self.constant = kwargs.get('constant', 0.01)

    def _get_default_ranker(self, corpus):
        return OncePerDocFrequencyRanker(corpus)

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

        Returnss
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
        in_target_cat = cat_X.sum(axis=0)/cat_X.shape[1]
        not_in_non_target_cat = (ncat_X.shape[1] - ncat_X.sum(axis=0))/ncat_X.shape[1]
        return (in_target_cat + not_in_non_target_cat).A1

    def get_name(self):
        return "Craig's Zeta"

