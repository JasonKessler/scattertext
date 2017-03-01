from unittest import TestCase

import numpy as np

from scattertext.Scalers import percentile_alphabetical


class TestPercentile_lexicographic(TestCase):
	def test_percentile_lexicographic(self):
		scores = [1, 1, 5, 18, 1, 3]
		text = ['c', 'a', 'five', 'eighteen', 'b', 'three']

		ranking = percentile_alphabetical(scores, text)
		np.testing.assert_array_almost_equal(ranking, np.array([0.4, 0, 0.8, 1., 0.2, 0.6]))
