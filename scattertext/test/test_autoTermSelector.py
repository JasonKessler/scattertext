from unittest import TestCase

from scattertext.AutoTermSelector import AutoTermSelector
from scattertext.test.test_TermDocMat import make_a_test_term_doc_matrix


class TestAutoTermSelector(TestCase):
	def test_reduce_terms(self):
		tdm = make_a_test_term_doc_matrix()
		scores = tdm.get_term_freq_df().sum(axis=1) % 10
		new_tdm = AutoTermSelector.reduce_terms(
			tdm, scores, num_term_to_keep=10)
		self.assertLessEqual(len(new_tdm.get_term_freq_df().index), 10)
		self.assertEqual(len(tdm.get_term_freq_df().index), 58)

	def test_get_selected_terms(self):
		tdm = make_a_test_term_doc_matrix()
		scores = tdm.get_term_freq_df().sum(axis=1) % 10
		selected_terms = AutoTermSelector.get_selected_terms(tdm, scores, num_term_to_keep=10)
		self.assertLessEqual(len(selected_terms), 10)
		self.assertEqual(len(tdm.get_term_freq_df().index), 58)

