from unittest import TestCase

from scattertext import TermDocMatrixFilter
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix


class TestPMIFiltering(TestCase):
	def test_main(self):
		term_doc_mat = get_hamlet_term_doc_matrix()
		pmi_filter = TermDocMatrixFilter(pmi_threshold_coef=4, min_freq=3)
		filtered_term_doc_mat = pmi_filter.filter(term_doc_mat)
		print('term_doc_mat_df_len', len(term_doc_mat.get_term_freq_df()))
		print('filtered_term_doc_mat_df_len', len(filtered_term_doc_mat.get_term_freq_df()))
		print(term_doc_mat.get_term_freq_df())
		print(filtered_term_doc_mat.get_term_freq_df())
		self.assertLessEqual(len(filtered_term_doc_mat.get_term_freq_df()), len(term_doc_mat.get_term_freq_df()))