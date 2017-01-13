import json
from unittest import TestCase

import numpy as np

from scattertext import ScatterChart
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_term_doc_mat


class TestScatterChart(TestCase):
	def test_to_json(self):
		tdm = build_hamlet_jz_term_doc_mat()
		# with self.assertRaises(NoWordMeetsTermFrequencyRequirementsError):
		#	ScatterChart(term_doc_matrix=tdm).to_dict('hamlet')
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0)
		     .to_dict('hamlet'))
		self.assertEqual(set(j.keys()), set(['info', 'data']))
		self.assertEqual(set(j['info'].keys()),
		                 set(['not_category_name', 'category_name',
		                      'category_terms', 'not_category_terms', 'category_internal_name']))
		expected = {"x": 0.0,
		            "y": 0.42,
		            "term": "art",
		            "cat25k": 758,
		            "ncat25k": 0, 's': 0.5, 'os': 3}
		datum = j['data'][0]
		for var in ['x', 'y', 'cat25k', 'ncat25k', 's']:
			np.testing.assert_almost_equal(expected[var], datum[var])
		self.assertEqual(expected.keys(), datum.keys())
		self.assertEqual(expected['term'], datum['term'])
		json.dumps(j)

	def test_max_terms(self):
		tdm = build_hamlet_jz_term_doc_mat()
		# with self.assertRaises(NoWordMeetsTermFrequencyRequirementsError):
		#	ScatterChart(term_doc_matrix=tdm).to_dict('hamlet')
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  max_terms=2)
		     .to_dict('hamlet'))
		self.assertEqual(2, len(j['data']))

		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  max_terms=10)
		     .to_dict('hamlet'))
		self.assertEqual(10, len(j['data']))


		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  max_terms=10000)
		     .to_dict('hamlet'))
		self.assertEqual(51, len(j['data']))

		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  max_terms=None)
		     .to_dict('hamlet'))
		self.assertEqual(51, len(j['data']))
