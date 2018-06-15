from unittest import TestCase

import numpy as np

from scattertext.domain.CombineDocsIntoDomains import CombineDocsIntoDomains
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix


class TestCombineDocsIntoDomains(TestCase):
	def test_get_new_term_doc_mat(self):
		hamlet = get_hamlet_term_doc_matrix()
		domains = np.arange(hamlet.get_num_docs()) % 3
		tdm = CombineDocsIntoDomains(hamlet).get_new_term_doc_mat(domains)
		self.assertEquals(tdm.shape, (3, hamlet.get_num_terms()))
		self.assertEquals(tdm.sum(), hamlet.get_term_doc_mat().sum())