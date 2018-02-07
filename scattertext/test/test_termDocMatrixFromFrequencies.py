from unittest import TestCase

import numpy as np
import pandas as pd

from scattertext.TermDocMatrixFromFrequencies import TermDocMatrixFromFrequencies


class TestTermDocMatrixFromFrequencies(TestCase):
	def test_build(self):
		term_freq_df = pd.DataFrame({
			'term': ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'],
			'A': [6, 3, 3, 3, 5, 0, 0],
			'B': [6, 3, 3, 3, 5, 1, 1],
		}).set_index('term')[['A', 'B']]
		term_doc_mat = TermDocMatrixFromFrequencies(term_freq_df).build()
		self.assertEqual(list(term_doc_mat.get_categories()), ['A', 'B'])
		self.assertEqual(list(term_doc_mat.get_terms()),
		                 ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'])
		np.testing.assert_array_equal(term_freq_df.values,
		                              term_doc_mat.get_term_freq_df().values)