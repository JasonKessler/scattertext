import pandas as pd
from scipy.stats import power_divergence

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class LogLikelihoodRatio(CorpusBasedTermScorer):
    """
    Log likelihood ratio (inspired by https://github.com/Zeta-and-Company/pydistinto/blob/main/scripts/measures/LLR.py)

    """
    def _set_scorer_args(self, *args): pass

    def get_scores(self, *args) -> pd.Series:
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        X = self._get_X() > 0
        cat_X, ncat_X = self._get_cat_and_ncat(X)
        return pd.Series(self._get_llr_score(cat_X, ncat_X).statistic, index=self._get_terms())

    def get_score_df(self, *args) -> pd.DataFrame:
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        X = self._get_X() > 0
        cat_X, ncat_X = self._get_cat_and_ncat(X)
        score = self._get_llr_score(cat_X, ncat_X)
        return pd.DataFrame({
            'Term': self._get_terms(),
            'Base': cat_X.sum(axis=0).A1,
            'Counter': ncat_X.sum(axis=0).A1,
            'Score': score.statistic,
            'PValue': score.pvalue
        }).set_index('Term')

    def _get_terms(self):
        return self.corpus_.get_terms(use_metadata=self.use_metadata_)

    def _get_llr_score(self, cat_X, ncat_X):
        a = cat_X.sum(axis=0).A1
        b = ncat_X.sum(axis=0).A1
        exp1 = (sum(a) * (a + b)) / (sum(a) + sum(b))
        exp2 = (sum(b) * (a + b)) / (sum(a) + sum(b))
        return power_divergence(
            [a, b],
            f_exp=[exp1, exp2]
        )

    def get_name(self):
        return 'Log likelihood ratio'
