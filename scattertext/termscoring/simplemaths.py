import numpy as np
import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class SimpleMaths(CorpusBasedTermScorer):
    """
    Simple Maths from Kilgariff (2009).


    Stephanie Evert. 2023. Measuring Keyness. https://osf.io/x8z9n.

    Adam Kilgariff. 2009. Simple Maths for Keywords. Proc. Corpus Linguistics.
    https://www.semanticscholar.org/paper/Simple-Maths-for-Keywords-Kilgarriff/69bd0a8a964e9b3b0b4394fe0d9d602d6a5a0453
    """

    def _set_scorer_args(self, **kwargs):
        self.lambda_ = kwargs.get('lambda_', 1)
        self.log_ = kwargs.get('log', False)
        self.coef_ = kwargs.get('coef', 1e6)

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

        p1 = f1 / N1
        p2 = f2 / N2
        res = (self.coef_ * p1 + self.lambda_) / (self.coef_ * p2 + self.lambda_)
        if self.log_:
            res = np.log(res) / np.log(2)
        return pd.Series(res, index=self._get_terms())

    def get_name(self):
        return 'Simple Maths'
