from unittest import TestCase

import pandas as pd
import numpy as np

from scattertext.termscoring.RelativeEntropy import RelativeEntropy
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestRelativeEntropy(TestCase):
	@classmethod
	def setUpClass(cls):
		cls.corpus = build_hamlet_jz_corpus()

	def test_get_scores(self):
		result = RelativeEntropy(self.corpus).set_categories('hamlet').get_scores()
		self.assertEquals(type(result), pd.Series)
		np.testing.assert_array_equal(pd.np.array(result.index), self.corpus.get_terms())

	def test_get_name(self):
		self.assertEquals(RelativeEntropy(self.corpus).set_categories('hamlet').get_name(), 'Frankhauser Relative Entropy')
