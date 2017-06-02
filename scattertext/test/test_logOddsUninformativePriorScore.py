from unittest import TestCase

import numpy as np

from scattertext.termscoring.LogOddsUniformativePriorScore import LogOddsUninformativePriorScore


class TestLogOddsUninformativePriorScore(TestCase):
	def test_get_score(self):
		cat_counts, not_cat_counts = self._get_counts()
		scores = LogOddsUninformativePriorScore.get_score(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores,
		                               np.array([0.4447054, 0.9433088, 0.4447054, -0.9971462]))

	def test_get_score_threshold(self):
		cat_counts, not_cat_counts = self._get_counts()
		scores = LogOddsUninformativePriorScore.get_thresholded_score(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores,
		                               np.array([0., 0.9433088, 0., -0.9971462]))

	def test__turn_pvals_into_scores(self):
		p_vals = np.array([0.01, 0.99, 0.5, 0.1, 0.9])
		scores = LogOddsUninformativePriorScore._turn_pvals_into_scores(p_vals)
		np.testing.assert_almost_equal(scores, [0.98, -0.98, -0., 0.8, -0.8])

	def test__turn_counts_into_matrix(self):
		cat_counts, not_cat_counts = self._get_counts()
		X = LogOddsUninformativePriorScore._turn_counts_into_matrix(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(X, np.array([[1, 100],
		                                            [5, 510],
		                                            [1, 100],
		                                            [9, 199]]))

	def _get_counts(self):
		cat_counts = np.array([1, 5, 1, 9])
		not_cat_counts = np.array([100, 510, 100, 199])
		return cat_counts, not_cat_counts
