from unittest import TestCase

import pandas as pd

from scattertext.TermDocMatrixFromFrequencies import TermDocMatrixFromFrequencies
from scattertext.termcompaction.TermCompaction import CompactTerms


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
		new_tdm = CompactTerms(term_doc_mat, minimum_term_count=2).compact()
		self.assertEqual(term_doc_mat.get_terms(), ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'])
		self.assertEqual(set(new_tdm.get_terms()),
		                 set(term_doc_mat.get_terms()) - {'c', 'e b', 'e'})
		new_tdm = CompactTerms(term_doc_mat, minimum_term_count=1).compact()
		self.assertEqual(set(new_tdm.get_terms()),
		                 set(term_doc_mat.get_terms()) - {'c', 'e'})
