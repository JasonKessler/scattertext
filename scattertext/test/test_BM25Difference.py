from unittest import TestCase

import pandas as pd

from scattertext.termscoring.BM25Difference import BM25Difference
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestBM25Difference(TestCase):
	@classmethod
	def setUpClass(cls):
		cls.corpus = build_hamlet_jz_corpus()

	def test_get_scores(self):
		result = BM25Difference(self.corpus).set_categories('hamlet').get_scores()
		self.assertEquals(type(result), pd.Series)
		pd.np.testing.assert_array_equal(pd.np.array(result.index), self.corpus.get_terms())

	def test_get_name(self):
		self.assertEquals(BM25Difference(self.corpus).set_categories('hamlet').get_name(), 'BM25 difference')
