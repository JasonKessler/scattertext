from unittest import TestCase

import pandas as pd

from scattertext.TermDocMatrixFromFrequencies import TermDocMatrixFromFrequencies
from scattertext.termcompaction.CompactTerms import CompactTerms


class TestCompactTerms(TestCase):
	def test_get_term_indices_to_compact(self):
		'''
		term_doc_matrix = TermDocMatrixFromPandas(ConventionData2012().get_data(),
		                                          category_col='party',
		                                          text_col='text',
		                                          nlp=whitespace_nlp_with_sentences).build()
		term_freq_df = term_doc_matrix.get_term_freq_df()
		'''
		term_doc_mat = TermDocMatrixFromFrequencies(pd.DataFrame({
			'term': ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'],
			'A freq': [6, 3, 3, 3, 5, 0, 0],
			'B freq': [6, 3, 3, 3, 5, 1, 1],
		}).set_index('term')).build()
		new_tdm = CompactTerms(minimum_term_count=2).compact(term_doc_mat)
		self.assertEqual(term_doc_mat.get_terms(), ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'])
		self.assertEqual(set(new_tdm.get_terms()),
		                 set(term_doc_mat.get_terms()) - {'c', 'e b', 'e'})
		new_tdm = CompactTerms(minimum_term_count=1).compact(term_doc_mat)
		self.assertEqual(set(new_tdm.get_terms()),
		                 set(term_doc_mat.get_terms()) - {'c', 'e'})
		term_doc_mat = TermDocMatrixFromFrequencies(pd.DataFrame({
			'term': ['a', 'a b', 'b'],
			'A freq': [5, 4, 8],
			'B freq': [1, 1, 1],
		}).set_index('term')).build()
		self.assertEqual(set(CompactTerms(minimum_term_count=0, slack=0).compact(term_doc_mat).get_terms()), set(['a', 'a b', 'b']))
		self.assertEqual(set(CompactTerms(minimum_term_count=0, slack=2).compact(term_doc_mat).get_terms()), set(['b', 'a b']))
