from unittest import TestCase

import pandas as pd

from scattertext.termscoring.ZScores import ZScores
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestZScores(TestCase):
	@classmethod
	def setUpClass(cls):
		cls.corpus = build_hamlet_jz_corpus()

	def test_get_scores(self):
		result = ZScores(self.corpus).set_categories('hamlet').get_scores()
		self.assertEquals(type(result), pd.Series)
		pd.np.testing.assert_array_equal(pd.np.array(result.index), self.corpus.get_terms())

	def test_get_name(self):
		self.assertEquals(ZScores(self.corpus).set_categories('hamlet').get_name(), "Z-Score from Welch's T-Test")
