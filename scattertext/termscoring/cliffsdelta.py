import pdb

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from scipy.special import ndtri

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class CliffsDelta(CorpusBasedTermScorer):
    """
    Cliff's Delta from Cliff (1993).


    Cliff, N. (1993). Dominance statistics: Ordinal analyses to answer ordinal questions.
    Psychological Bulletin, 114(3), 494–509.

    https://real-statistics.com/non-parametric-tests/mann-whitney-test/cliffs-delta/ used as a resource
    """

    def _set_scorer_args(self, alpha: float = 0.05):
        self.alpha = alpha

    def get_scores(self, *args) -> pd.Series:
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        score_df = self.get_score_df()
        return score_df['Metric']

    def get_score_df(self, label_append=''):
        cat_X, ncat_X = self._get_cat_and_ncat(self._get_X())
        catXnorm = cat_X / cat_X.sum(axis=1)
        ncatXnorm = ncat_X / ncat_X.sum(axis=1)
        m = catXnorm.shape[0]
        n = ncatXnorm.shape[0]
        data = []
        for i, term in tqdm(enumerate(self._get_terms()), total=len(self._get_terms())):
            cati = np.repeat(catXnorm[:, i], n, axis=1).ravel().A1
            ncati = np.repeat(ncatXnorm[:, i], m, axis=1).T.ravel().A1
            deltai = np.zeros(n * m)
            deltai[cati > ncati] = 1
            deltai[cati < ncati] = -1
            delta = deltai.sum() / (m * n)
            deltars = deltai.reshape((n, m))
            delta_r = deltars.sum(axis=0) / n
            delta_c = deltars.sum(axis=1) / m
            sd = np.sqrt(
                (
                        m ** 2 * ((delta_r - delta) ** 2).sum()
                        + n ** 2 * ((delta_c - delta) ** 2).sum()
                        - ((deltai - delta) ** 2).sum()
                ) / (m * n * (m - 1) * (n - 1))
            )
            zcrit = ndtri(self.alpha)
            lo = (delta - delta ** 3 - zcrit * sd * np.sqrt(1 - 2 * delta ** 2 + delta ** 4 + (zcrit * delta) ** 2)) / (
                    1 - delta ** 2 - (zcrit * delta) ** 2
            )

            hi = (delta - delta ** 3 + zcrit * sd * np.sqrt(1 - 2 * delta ** 2 + delta ** 4 + (zcrit * delta) ** 2)) / (
                    1 - delta ** 2 - (zcrit * delta) ** 2
            )
            data.append({
                'term': term,
                'Metric': delta,
                'Stddev': sd,
                f'Low-{(1-self.alpha) * 100}% CI': lo,
                f'High-{(1-self.alpha) * 100}% CI': hi,
            })
        return pd.DataFrame(data).set_index('term').assign(
            TermCount1=cat_X.sum(axis=0).A1,
            TermCount2=ncat_X.sum(axis=0).A1,
            DocCount1=(cat_X > 0).sum(axis=0).A1,
            DocCount2=(ncat_X > 0).sum(axis=0).A1
        )

    def get_name(self):
        return "Cliff's Delta"
