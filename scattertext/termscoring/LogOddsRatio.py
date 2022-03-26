import numpy as np

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class LogOddsRatio(CorpusBasedTermScorer):

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
        if self.tdf_ is None:
            raise Exception("Use set_categories('category name', ['not category name', ...]) " +
                            "to set the category of interest")

        y_i = self.tdf_['cat']
        y_j = self.tdf_['ncat']
        n_i, n_j = y_i.sum(), y_j.sum()
        delta_i_j = (np.log((y_i + self.constant) / (self.constant + n_i - y_i))
                     - np.log((y_j + self.constant) / (self.constant + n_j - y_j)))
        return delta_i_j

    def get_name(self):
        return 'Smoothed Log Odds Ratio'

