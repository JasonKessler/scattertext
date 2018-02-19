from unittest import TestCase
import pandas as pd
from scattertext.TermDocMatrixFromFrequencies import TermDocMatrixFromFrequencies
from scattertext.termcompaction.ClassPercentageCompactor import ClassPercentageCompactor


class TestClassPercentageCompactor(TestCase):
	def test_compact(self):
		term_doc_mat = TermDocMatrixFromFrequencies(pd.DataFrame({
			'term': ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'],
			'A freq': [6, 3, 3, 3, 50000, 0, 0],
			'B freq': [600000, 3, 30, 3, 50, 1, 1],
		}).set_index('term')).build()
		new_tdm = ClassPercentageCompactor(term_count=10000).compact(term_doc_mat)
		self.assertEqual(term_doc_mat.get_terms(),  ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'])
		self.assertEqual(set(new_tdm.get_terms()),
		                 {'a','b'})


