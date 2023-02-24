import numpy as np
import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


def lg(x): return np.log(x) / np.log(2)


class DeltaJSDivergence(object):
    def __init__(self, pi1=0.5, pi2=0.5):
        assert pi1 + pi2 == 1
        self.pi1 = pi1
        self.pi2 = pi2

    def get_scores(self, a, b):
        # via https://arxiv.org/pdf/2008.02250.pdf eqn 1
        p1 = 0.001 + a / np.sum(a)
        p2 = 0.001 + b / np.sum(b)
        pi1, pi2 = self.pi1, self.pi2
        m = pi1 * p1 + pi2 * p2

        def lg(x): return np.log(x) / np.log(2)

        return m * lg(1 / m) - (pi1 * p2 * lg(1 / p1) + pi2 * p2 * lg(1 / p2))

    def get_default_score(self):
        return 0

    def get_name(self):
        return 'JS Divergence Shift'


class DeltaJSDivergenceScorer(CorpusBasedTermScorer):
    def _set_scorer_args(self, **kwargs):
        self.pi1 = kwargs.get('pi1', 0.5)
        self.pi2 = kwargs.get('pi2', 0.5)
        assert self.pi1 + self.pi2 == 1


    def get_score_df(self):
        return pd.DataFrame({'Score': self.get_scores()})

    def get_scores(self):
        rank_df = self.term_ranker_.set_non_text(self.use_metadata_).get_ranks('')
        focus = rank_df[str(self.category_name)].values
        background = rank_df[
            [str(c) for c in self.corpus_.get_categories() if str(c) in self.not_category_names]
        ].sum(axis=1).values
        scores = DeltaJSDivergence(self.pi1, self.pi2).get_scores(a=focus, b=background)
        return pd.Series(scores, index=self._get_index())

    def get_default_score(self):
        return 0

    def get_name(self):
        return 'JS Divergence Shift'
