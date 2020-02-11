from unittest import TestCase

import pandas as pd
import numpy as np

from scattertext import OncePerDocFrequencyRanker
from scattertext.termscoring.ZScores import ZScores
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus, build_hamlet_jz_corpus_with_meta


class TestZScores(TestCase):
	@classmethod
	def setUpClass(cls):
		cls.corpus = build_hamlet_jz_corpus()

	def test_get_scores(self):
		result = ZScores(self.corpus).set_categories('hamlet').get_scores()
		self.assertEquals(type(result), pd.Series)
		np.testing.assert_array_equal(np.array(result.index), self.corpus.get_terms())

	def test_get_name(self):
		self.assertEquals(ZScores(self.corpus).set_categories('hamlet').get_name(), "Z-Score from Welch's T-Test")

	def test_get_ranks_meta(self):
		corpus = build_hamlet_jz_corpus_with_meta()
		self.assertEquals(ZScores(corpus)
						  .set_term_ranker(OncePerDocFrequencyRanker)
						  .set_categories('hamlet').get_name(), "Z-Score from Welch's T-Test")
