import numpy as np
import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class LogRelativeRisk(CorpusBasedTermScorer):
    """
    LogRatio from Hardie 2014

    Stephanie Evert. 2023. Measuring Keyness. https://osf.io/x8z9n.

    """

    def _set_scorer_args(self, **kwargs):
        self.lambda_ = kwargs.get('lambda_', 0.01)

    def get_scores(self, *args) -> pd.Series:
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        cat_X, ncat_X = self._get_cat_and_ncat(self._get_X())
        N1 = self._get_cat_size()
        N2 = self._get_ncat_size()
        if len(args) == 0:
            f1 = cat_X.sum(axis=0).A1
            f2 = ncat_X.sum(axis=0).A1
        else:
            f1, f2 = self.__get_f1_f2_from_args(args)

        res = np.log((f1 + self.lambda_)/N1)/np.log(2) - np.log((f2 + self.lambda_)/N2)/np.log(2)
        return pd.Series(res, index=self._get_terms())

    def get_name(self):
        return 'Log Relative Risk'
