import numpy as np

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class FrequencyScorer(CorpusBasedTermScorer):

    def _set_scorer_args(self, **kwargs):
        self.constant = kwargs.get('constant', 0.01)

    def get_scores(self, *args):
        '''
        Returns category frequencies

        Returns
        -------
        np.array, scores
        '''
        if self.tdf_ is None:
            raise Exception("Use set_categories('category name', ['not category name', ...]) " +
                            "to set the category of interest")

        y_i = self.tdf_['cat']
        return y_i

    def get_name(self):
        return 'Frequency'
