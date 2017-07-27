from unittest import TestCase

import numpy as np

from scattertext.termscoring.ScaledFScore import ScaledFScore


class TestScaledFScore(TestCase):
	def test_get_scores(self):
		cat_counts, not_cat_counts = self._get_counts()
		scores = ScaledFScore.get_scores(cat_counts, not_cat_counts, beta=1.)
		np.testing.assert_almost_equal(scores,
		                               np.array([0.2689108, 0., 0.2689108, 0.1266617, 1.,
		                                         0.5, 0.5590517, 0.5, 0.5, 0.5720015]))

	def test_get_scores_zero_all_same(self):
		cat_counts = np.array([0, 0, 0, 0, 0, 0, 1, 2])
		not_cat_counts = np.array([1, 1, 2, 1, 1, 1, 1, 2])
		scores = ScaledFScore.get_scores(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores, [0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.5, 1.])

	def test_get_scores_zero_median(self):
		cat_counts = np.array([0, 0, 0, 0, 0, 0, 1, 2])
		not_cat_counts = np.array([1, 1, 2, 1, 1, 1, 1, 3])
		ScaledFScore.get_scores(cat_counts, not_cat_counts)

	def get_scores_for_category(self):
		cat_counts, not_cat_counts = self._get_counts()
		scores = ScaledFScore.get_scores_for_category(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores,
		                               [0.23991183969723384, 0.24969810634506373, 0.23991183969723384,
		                                0.27646711056272855, 0.92885244834997516, 0.42010144843632563,
		                                0.49166017105966719, 0.0, 0.0, 0.50262304057984664])

	def _get_counts(self):
		cat_counts = np.array([1, 5, 1, 9, 100, 1, 1, 0, 0, 2])
		not_cat_counts = np.array([100, 510, 100, 199, 0, 1, 0, 1, 1, 0])

		return cat_counts, not_cat_counts
