from unittest import TestCase

import numpy as np

from scattertext import ScatterChart
from scattertext.ScatterChart import NoWordMeetsTermFrequencyRequirementsError
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_term_doc_mat


class TestScatterChart(TestCase):
	def test_to_json(self):
		tdm = build_hamlet_jz_term_doc_mat()
		with self.assertRaises(NoWordMeetsTermFrequencyRequirementsError):
			ScatterChart(term_doc_matrix=tdm).to_dict('hamlet')
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0)
		     .to_dict('hamlet'))
		expected = {"x": 0.0, "y": 0.4081632653, "term": "and", "cat25k": 758, "ncat25k": 0, 's': 0.5}
		for var in ['x','y','cat25k','ncat25k', 's']:
			np.testing.assert_almost_equal(expected[var], j[0][var])
		self.assertEqual(expected.keys(), j[0].keys())
		self.assertEqual(expected['term'], j[0]['term'])
