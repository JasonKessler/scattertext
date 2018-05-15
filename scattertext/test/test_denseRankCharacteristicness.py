from unittest import TestCase

from scattertext.characteristic.DenseRankCharacteristicness import DenseRankCharacteristicness
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix


class TestDenseRankCharacteristicness(TestCase):
	def test_get_scores(self):
		c = get_hamlet_term_doc_matrix()
		zero_point, scores = DenseRankCharacteristicness().get_scores(c)
		self.assertGreater(zero_point, 0)
		self.assertLessEqual(zero_point, 1)
		self.assertGreater(len(scores), 100)
