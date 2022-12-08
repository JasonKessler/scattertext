import pandas as pd
from scipy.stats import norm, mannwhitneyu

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class RankSum(CorpusBasedTermScorer):
    """
    Wilcoxon Rank Sum (inspired by https://github.com/Zeta-and-Company/pydistinto/blob/main/scripts/measures/wilcoxon_ranksum.py)
    Pseudo counts of 0.0001 are added to each document.
    """
    def _set_scorer_args(self, **args):
        self.verbose = args.get('verbose', False)

    def get_scores(self, *args):
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        return self.get_score_df().Score

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
        cat_X = cat_X.todense().T
        cat_X = cat_X/cat_X.sum(axis=0)
        ncat_X = ncat_X.todense().T
        ncat_X = ncat_X / ncat_X.sum(axis=0)

        it = range(cat_X.shape[0])
        if self.verbose:
            from tqdm.auto import tqdm
            it = tqdm(range(cat_X.shape[0]), total=cat_X.shape[0])
        scores = []
        for i in it:
            a = cat_X[i].A1 + [0.0001]
            b = ncat_X[i].A1 + [0.0001]
            stat = mannwhitneyu(a, b)
            scores.append([stat.statistic, stat.pvalue, a.sum(), b.sum()])
        return pd.DataFrame(scores, columns=['Score', 'PValue', 'Base', 'Counter']).assign(
            Term=self.corpus_.get_terms(),
            Z=lambda df: norm.ppf(df.PValue),
        ).set_index('Term')

    def get_name(self):
        return 'Man-Whitney U'
