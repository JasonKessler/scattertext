import sys
from unittest import TestCase

import numpy as np

from scattertext import LogOddsRatioUninformativeDirichletPrior
from scattertext import ScatterChart
from scattertext.ScatterChart import CoordinatesNotRightException, TermDocMatrixHasNoMetadataException
from scattertext.test.test_semioticSquare import get_test_corpus
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
		                 set(['not_category_name',
		                      'category_name',
		                      'category_terms',
		                      'not_category_terms',
		                      'category_internal_name',
		                      'not_category_internal_names',
		                      'neutral_category_internal_names',
		                      'extra_category_internal_names',
		                      'categories']))
		expected = {"x": 0.0,
		            "y": 0.42,
		            'ox': 0,
		            'oy': 0.42,
		            "term": "art",
		            "cat25k": 758,
		            "ncat25k": 0,
		            "neut25k": 0,
		            'neut': 0,
		            "extra25k": 0,
		            'extra': 0,
		            's': 0.5,
		            'os': 3,
		            'bg': 3}
		datum = self._get_data_example(j)
		for var in ['cat25k', 'ncat25k']:
			np.testing.assert_almost_equal(expected[var], datum[var], decimal=1)
		self.assertEqual(set(expected.keys()), set(datum.keys()))
		self.assertEqual(expected['term'], datum['term'])

	def test_resuse_is_disabled(self):
		corpus = get_test_corpus()
		sc = ScatterChart(term_doc_matrix=corpus, minimum_term_frequency=0)
		sc.to_dict('hamlet')
		with self.assertRaises(Exception):
			sc.to_dict('hamlet')

	def test_multi_categories(self):
		corpus = get_test_corpus()
		j_vs_all = ScatterChart(term_doc_matrix=corpus, minimum_term_frequency=0) \
			.to_dict('hamlet')
		j_vs_swift = ScatterChart(term_doc_matrix=corpus, minimum_term_frequency=0) \
			.to_dict('hamlet', not_categories=['swift'])
		self.assertNotEqual(set(j_vs_all['info']['not_category_internal_names']),
		                    set(j_vs_swift['info']['not_category_internal_names']))
		self.assertEqual(j_vs_all['info']['categories'], corpus.get_categories())
		self.assertEqual(j_vs_swift['info']['categories'], corpus.get_categories())

	def test_title_case_names(self):
		tdm = build_hamlet_jz_term_doc_mat()
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0)
		     .to_dict('hamlet', 'HAMLET', 'NOT HAMLET'))
		self.assertEqual(j['info']['category_name'], 'HAMLET')
		self.assertEqual(j['info']['not_category_name'], 'NOT HAMLET')
		tdm = build_hamlet_jz_term_doc_mat()
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0)
		     .to_dict('hamlet', 'HAMLET', 'NOT HAMLET', title_case_names=True))
		self.assertEqual(j['info']['category_name'], 'Hamlet')
		self.assertEqual(j['info']['not_category_name'], 'Not Hamlet')

	def _get_data_example(self, j):
		return [t for t in j['data'] if t['term'] == 'art'][0]

	def test_terms_to_include(self):
		tdm = build_hamlet_jz_term_doc_mat()
		terms_to_include = list(sorted(['both worlds', 'thou', 'the', 'of', 'st', 'returned', 'best', ]))
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  terms_to_include=terms_to_include)
		     .to_dict('hamlet', 'HAMLET', 'NOT HAMLET'))
		self.assertEqual(list(sorted(t['term'] for t in j['data'])), terms_to_include)

	def test_p_vals(self):
		tdm = build_hamlet_jz_term_doc_mat()
		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  term_significance=LogOddsRatioUninformativeDirichletPrior())
		     .to_dict('hamlet'))
		datum = self._get_data_example(j)
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
			scatter_chart.inject_coordinates(x, y / y.max())
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(x / x.max(), y)
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(-x / x.max(), -y / y.max())
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(-x / x.max(), y / y.max())
		with self.assertRaises(CoordinatesNotRightException):
			scatter_chart.inject_coordinates(x / x.max(), -y / y.max())
		scatter_chart.inject_coordinates(x / x.max(), y / y.max())

	def test_inject_metadata_term_lists(self):
		tdm = build_hamlet_jz_term_doc_mat()
		scatter_chart = ScatterChart(term_doc_matrix=tdm,
		                             minimum_term_frequency=0)
		with self.assertRaises(TermDocMatrixHasNoMetadataException):
			scatter_chart.inject_metadata_term_lists({'blah': ['a', 'adsf', 'asfd']})
		scatter_chart = ScatterChart(term_doc_matrix=build_hamlet_jz_corpus_with_meta(),
		                 minimum_term_frequency=0,
		                 use_non_text_features=True)

		with self.assertRaises(TypeError):
			scatter_chart.inject_metadata_term_lists({'blash': [3,1]})
		with self.assertRaises(TypeError):
			scatter_chart.inject_metadata_term_lists({3: ['a','b']})
		with self.assertRaises(TypeError):
			scatter_chart.inject_metadata_term_lists({'a': {'a','b'}})
		with self.assertRaises(TypeError):
			scatter_chart.inject_metadata_term_lists(3)
		self.assertEqual(type(scatter_chart.inject_metadata_term_lists({'a': ['a', 'b']})), ScatterChart)
		j = scatter_chart.to_dict('hamlet')
		self.assertEqual(set(j.keys()), set(['info', 'data', 'metalists']))
		self.assertEqual(set(j['info'].keys()),
		                 set(['not_category_name',
		                      'category_name',
		                      'category_terms',
		                      'not_category_terms',
		                      'category_internal_name',
		                      'not_category_internal_names',
		                      'extra_category_internal_names',
		                      'neutral_category_internal_names',
		                      'categories']))

	def test_inject_metadata_descriptions(self):
		tdm = build_hamlet_jz_corpus_with_meta()
		scatter_chart = ScatterChart(term_doc_matrix=tdm, minimum_term_frequency=0)
		with self.assertRaises(AssertionError):
			scatter_chart.inject_metadata_descriptions(3323)
		if (sys.version_info > (3, 0)):
			with self.assertRaisesRegex(Exception, 'The following meta data terms are not present: blah'):
				scatter_chart.inject_metadata_descriptions({'blah': 'asjdkflasdjklfsadjk jsdkafsd'})
			with self.assertRaisesRegex(Exception, 'The following meta data terms are not present: cat2'):
				scatter_chart.inject_metadata_descriptions({'cat1': 'asjdkflasdjklfsadjk jsdkafsd', 'cat2': 'asdf'})
		assert scatter_chart == scatter_chart.inject_metadata_descriptions({'cat1': 'asjdkflasdjklfsadjk jsdkafsd'})
		j = scatter_chart.to_dict('hamlet')
		self.assertEqual(set(j.keys()), set(['info', 'data', 'metadescriptions']))

	def test_inject_coordinates_original(self):
		tdm = build_hamlet_jz_term_doc_mat()
		freq_df = tdm.get_term_freq_df()
		scatter_chart = ScatterChart(term_doc_matrix=tdm,
		                             minimum_term_frequency=0)
		x = freq_df[freq_df.columns[1]].astype(np.float)
		y = freq_df[freq_df.columns[0]].astype(np.float)
		scatter_chart.inject_coordinates(x / x.max(), y / y.max(), original_x=x, original_y=y)
		j = scatter_chart.to_dict('hamlet')
		self.assertEqual(j['data'][0].keys(),
		                 {'x', 'os', 'y', 'ncat25k', 'neut', 'cat25k', 'ox', 'neut25k', 'extra25k', 'extra', 'oy', 'term',
		                  's', 'bg'})
		and_term = [t for t in j['data'] if t['term'] == 'and'][0]
		self.assertEqual(and_term['ox'], 0)
		self.assertEqual(and_term['oy'], 1)

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
		                 set(['not_category_name',
		                      'category_name',
		                      'category_terms',
		                      'not_category_terms',
		                      'category_internal_name',
		                      'not_category_internal_names',
		                      'extra_category_internal_names',
		                      'neutral_category_internal_names',
		                      'categories']))
		self.assertEqual({t['term'] for t in j['data']}, {'cat1'}
		                 # {'cat4', 'cat9', 'cat5', 'cat0', 'cat3', 'cat2', 'cat1'}
		                 )

	def test_max_terms(self):
		tdm = build_hamlet_jz_term_doc_mat()
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
		                  pmi_threshold_coefficient=0,
		                  max_terms=10000)
		     .to_dict('hamlet'))
		self.assertEqual(len(tdm.get_term_freq_df()), len(j['data']))

		j = (ScatterChart(term_doc_matrix=tdm,
		                  minimum_term_frequency=0,
		                  pmi_threshold_coefficient=0,
		                  max_terms=None)
		     .to_dict('hamlet'))
		self.assertEqual(len(tdm.get_term_freq_df()), len(j['data']))
