import numpy as np
import pandas as pd
from scipy.stats import rankdata

from scattertext import CorpusBasedTermScorer


class RankDifferenceScorer(CorpusBasedTermScorer):
    def _set_scorer_args(self, **kwargs):
        '''
        method : {'average', 'min', 'max', 'dense', 'ordinal'}, optional
        '''
        self.method = kwargs.get('method', 'dense')

    def get_scores(self, *args):
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        if self.tdf_ is None:
            raise Exception("Use set_categories('category name', ['not category name', ...]) " +
                            "to set the category of interest")

        dense_rank_difference = self._dense_rank_difference(
            self.tdf_['cat'], self.tdf_['ncat']
        )

        if type(self.tdf_['cat']) == pd.Series:
            return pd.Series(
                dense_rank_difference,
                index=self.tdf_['cat'].index
            )
        return dense_rank_difference

    def _dense_rank_difference(self, a, b):
        a_ranks = rankdata(a, self.method)
        b_ranks = rankdata(b, self.method)
        to_ret = (a_ranks / np.max(a_ranks)) - (b_ranks / np.max(b_ranks))
        return to_ret

    def get_default_score(self):
        return 0

    def get_name(self):
        return 'Rank Difference'
