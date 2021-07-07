import numpy as np

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