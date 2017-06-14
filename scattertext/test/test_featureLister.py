from unittest import TestCase

from scattertext.FeatureOuput import FeatureLister
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus_with_meta


class TestFeatureList(TestCase):
	def test_main(self):
		tdm = build_hamlet_jz_corpus_with_meta()
		features = FeatureLister(tdm._mX,
		                         tdm._metadata_idx_store,
		                         tdm.get_num_docs()).output()
		expected  = [{'cat4': 2, 'cat3': 1}, {'cat4': 2}, {'cat5': 1, 'cat3': 2},
		                  {'cat6': 2, 'cat9': 1},
		                  {'cat4': 2, 'cat3': 1}, {'cat2': 1, 'cat1': 2},
		                  {'cat2': 2, 'cat5': 1},
		                  {'cat4': 1, 'cat3': 2}]
		expected = [{'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}]

		self.assertEqual(features,
		                 expected)
