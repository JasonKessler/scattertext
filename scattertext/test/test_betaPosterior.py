from unittest import TestCase
import numpy as np
import pandas as pd

from scattertext.termscoring.BetaPosterior import BetaPosterior
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestBetaPosterior(TestCase):
    def test_get_score_df(self):
        corpus = build_hamlet_jz_corpus()
        beta_posterior = BetaPosterior(corpus).set_categories('hamlet')
        score_df = beta_posterior.get_score_df()

        scores = beta_posterior.get_scores()
        np.testing.assert_almost_equal(scores[:5], [-0.3194860824225506, 1.0294085051562822, 1.0294085051562822,
                                                    1.234664219528909, 1.0294085051562822])

    def test_get_name(self):
        corpus = build_hamlet_jz_corpus()
        self.assertEqual(BetaPosterior(corpus).get_name(), 'Beta Posterior')
