import json
from unittest import TestCase

import numpy as np

from scattertext import LogOddsRatioUninformativeDirichletPrior
from scattertext import ScatterChart
from scattertext.ScatterChart import CoordinatesNotRightException
from scattertext.test.test_termDocMatrixFactory \
	import build_hamlet_jz_term_doc_mat, build_hamlet_jz_corpus_with_meta


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
		            "ncat25k": 0,
		            's': 0.5,
		            'os': 3,
		            'bg': 3}
		datum = self._get_data_example(j)
		for var in ['cat25k', 'ncat25k']:
			np.testing.assert_almost_equal(expected[var], datum[var], decimal=1)
		self.assertEqual(set(expected.keys()), set(datum.keys()))
		self.assertEqual(expected['term'], datum['term'])

	def _get_data_example(self, j):
		return [t for t in j['data'] if t['term'] == 'art'][0]

	def test_p_vals(self):
		tdm = build_hamlet_jz_term_doc_mat()
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  term_significance=LogOddsRatioUninformativeDirichletPrior())
		     .to_dict('hamlet'))
		datum = self._get_data_example(j)
		print(datum)
		self.assertIn('p', datum.keys())

	def test_inject_coordinates(self):
		tdm = build_hamlet_jz_term_doc_mat()
		freq_df = tdm.get_term_freq_df()
		scatter_chart = ScatterChart(term_doc_matrix=tdm,
		                             minimum_term_frequency=0)
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates([], [])
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(freq_df[freq_df.columns[0]], [])
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates([], freq_df[freq_df.columns[0]])
		x = freq_df[freq_df.columns[1]].astype(np.float)
		y = freq_df[freq_df.columns[0]].astype(np.float)
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(x, y)
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(x, y/y.max())
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(x/x.max(), y)
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(-x / x.max(), -y / y.max())
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(-x / x.max(), y / y.max())
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(x / x.max(), -y / y.max())
		scatter_chart.inject_coordinates(x / x.max(), y / y.max())

	def test_to_json_use_non_text_features(self):
		tdm = build_hamlet_jz_corpus_with_meta()
		# with self.assertRaises(NoWordMeetsTermFrequencyRequirementsError):
		#	ScatterChart(term_doc_matrix=tdm).to_dict('hamlet')
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  use_non_text_features=True)
		     .to_dict('hamlet'))
		self.assertEqual(set(j.keys()), set(['info', 'data']))
		self.assertEqual(set(j['info'].keys()),
		                 set(['not_category_name', 'category_name',
		                      'category_terms', 'not_category_terms',
		                      'category_internal_name']))
		self.assertEqual({t['term'] for t in j['data']}, {'cat1'}
		                 #{'cat4', 'cat9', 'cat5', 'cat0', 'cat3', 'cat2', 'cat1'}
		                 )
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
