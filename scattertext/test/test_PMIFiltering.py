from unittest import TestCase

import pandas as pd

from scattertext import TermDocMatrixFilter
from scattertext import TermDocMatrixFromPandas
from scattertext import whitespace_nlp
from scattertext.TermDocMatrixFilter import AtLeastOneCategoryHasNoTermsException, filter_bigrams_by_pmis, \
	unigrams_that_only_occur_in_one_bigram, filter_out_unigrams_that_only_occur_in_one_bigram
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix




class TestPMIFiltering(TestCase):
	def test_main(self):
		term_doc_mat = get_hamlet_term_doc_matrix()
		pmi_filter = TermDocMatrixFilter(pmi_threshold_coef=4,
		                                 minimum_term_freq=3)
		filtered_term_doc_mat = pmi_filter.filter(term_doc_mat)
		self.assertLessEqual(len(filtered_term_doc_mat.get_term_freq_df()), len(term_doc_mat.get_term_freq_df()))

	def _test_nothing_passes_filter_raise_error(self):
		term_doc_mat = get_hamlet_term_doc_matrix()
		pmi_filter = TermDocMatrixFilter(pmi_threshold_coef=4000,
		                                 minimum_term_freq=3000)
		with self.assertRaises(AtLeastOneCategoryHasNoTermsException):
			pmi_filter.filter(term_doc_mat)

	def test_filter_bigrams_by_pmis(self):
		term_doc_mat = get_hamlet_term_doc_matrix()
		df = term_doc_mat.get_term_freq_df()
		filtered_df = filter_bigrams_by_pmis(df, threshold_coef=3)
		self.assertLess(len(filtered_df), len(df))

	def test_unigrams_that_only_occur_in_one_bigram(self):
		bigrams = set(['the cat', 'the saw', 'horses are', 'are pigs', 'pigs horses'])
		expected = {'cat', 'saw'}
		self.assertEqual(expected, unigrams_that_only_occur_in_one_bigram(bigrams))

	def test_filter_out_unigrams_that_only_occur_in_one_bigram(self):
		bigrams = ['the cat', 'the saw', 'horses are', 'are pigs', 'pigs horses']
		df = TermDocMatrixFromPandas(
			data_frame=pd.DataFrame({'text': bigrams,
			                         'category': ['a', 'a', 'a', 'b', 'b']}),
			category_col='category',
			text_col='text',
			nlp=whitespace_nlp
		).build().get_term_freq_df()
		new_df = filter_out_unigrams_that_only_occur_in_one_bigram(df)
		self.assertFalse('cat' in new_df.index)
		self.assertFalse('saw' in new_df.index)
		self.assertTrue('the' in new_df.index)
		self.assertTrue('horses' in new_df.index)
		self.assertTrue('pigs' in new_df.index)
		self.assertEqual(set(bigrams) & set(new_df.index), set(bigrams))