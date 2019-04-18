import random
from unittest import TestCase

import numpy as np

from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.test.test_semioticSquare import get_test_corpus
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus, build_hamlet_jz_corpus_with_meta, \
	build_hamlet_jz_corpus_with_alt_text


class TestScatterChartExplorer(TestCase):
	def test_to_dict(self):
		np.random.seed(0)
		random.seed(0)
		corpus = build_hamlet_jz_corpus()
		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
			.to_dict('hamlet'))
		self.assertEqual(set(j.keys()), set(['info', 'data', 'docs']))
		self.assertEqual(set(j['info'].keys()),
		                 set(['not_category_name', 'category_name',
		                      'category_terms', 'not_category_internal_names',
		                      'not_category_terms', 'category_internal_name',
		                      'categories', 'neutral_category_name',
		                      'extra_category_name',
		                      'neutral_category_internal_names',
		                      'extra_category_internal_names']))

		self.assertEqual(list(j['docs']['labels']),
		                 [0, 0, 0, 0, 1, 1, 1, 1])
		self.assertEqual(list(j['docs']['texts']),
		                 ["what art thou that usurp'st this time of night,",
		                  'together with that fair and warlike form',
		                  'in which the majesty of buried denmark',
		                  'did sometimes march? by heaven i charge thee, speak!',
		                  'halt! who goes there?', 'it is i sire tone from brooklyn.',
		                  'well, speak up man what is it?',
		                  'news from the east sire! the best of both worlds has returned!'])
		expected = {'y': 0.5, 'ncat': 0, 'ncat25k': 0, 'bg': 5,
		            'cat': 1, 's': 0.5, 'term': 'art', 'os': 0.5192, 'extra': 0, 'extra25k': 0,

		            'cat25k': 758, 'x': 0.06, 'neut': 0, 'neut25k': 0, 'ox': 5, 'oy': 3}

		actual = [t for t in j['data'] if t['term'] == 'art'][0]
		'''
		for var in expected.keys():
			try:
				#np.testing.assert_almost_equal(actual[var], expected[var],decimal=1)
			except TypeError:
				self.assertEqual(actual[var], expected[var])
		'''
		self.assertEqual(set(expected.keys()), set(actual.keys()))
		self.assertEqual(expected['term'], actual['term'])
		self.assertEqual(j['docs'].keys(), {'texts', 'labels', 'categories'})

		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
			.inject_term_metadata({'art': {'display': 'blah blah blah', 'color': 'red'}})
			.to_dict('hamlet'))

		actual = [t for t in j['data'] if t['term'] == 'art'][0]
		expected = {'y': 0.5, 'ncat': 0, 'ncat25k': 0, 'bg': 5,
		            'cat': 1, 's': 0.5, 'term': 'art', 'os': 0.5192, 'extra': 0, 'extra25k': 0,

		            'cat25k': 758, 'x': 0.06, 'neut': 0, 'neut25k': 0, 'ox': 5, 'oy': 3,
					'etc': {'display': 'blah blah blah', 'color': 'red'}}
		self.assertEqual(set(actual.keys()), set(expected.keys()))
		self.assertEqual(actual['etc'], expected['etc'])


		actual = [t for t in j['data'] if t['term'] != 'art'][0]
		self.assertEqual(set(actual.keys()), set(expected.keys()))
		self.assertEqual(actual['etc'], {})


	def test_hide_terms(self):
		corpus = build_hamlet_jz_corpus().get_unigram_corpus()
		terms_to_hide = ['thou', 'heaven']
		sc = (ScatterChartExplorer(corpus, minimum_term_frequency=0).hide_terms(terms_to_hide))
		self.assertEquals(type(sc), ScatterChartExplorer)
		j = sc.to_dict('hamlet', include_term_category_counts=True)
		self.assertTrue(all(['display' in t and t['display'] == False for t in j['data'] if t['term'] in terms_to_hide]))
		self.assertTrue(all(['display' not in t for t in j['data'] if t['term'] not in terms_to_hide]))

	def test_include_term_category_counts(self):
		corpus = build_hamlet_jz_corpus().get_unigram_corpus()
		j = (ScatterChartExplorer(corpus,
								  minimum_term_frequency=0)
			 .to_dict('hamlet', include_term_category_counts=True))
		self.assertEqual(set(j.keys()), set(['info', 'data', 'docs', 'termCounts']))
		self.assertEqual(len(j['termCounts']), corpus.get_num_categories())
		term_idx_set = set()
		for cat_counts in j['termCounts']:
			term_idx_set |= set(cat_counts.keys())
			self.assertTrue(all([freq >= docs for freq, docs in cat_counts.values()]))
		self.assertEqual(len(term_idx_set), corpus.get_num_terms())

	def test_multi_categories(self):
		corpus = get_test_corpus()
		j_vs_all = ScatterChartExplorer(corpus=corpus, minimum_term_frequency=0) \
			.to_dict('hamlet')
		j_vs_swift = ScatterChartExplorer(corpus=corpus, minimum_term_frequency=0) \
			.to_dict('hamlet', not_categories=['swift'])
		self.assertNotEqual(set(j_vs_all['info']['not_category_internal_names']),
		                    set(j_vs_swift['info']['not_category_internal_names']))
		self.assertEqual(list(j_vs_all['docs']['labels']), list(j_vs_swift['docs']['labels']))
		self.assertEqual(list(j_vs_all['docs']['categories']), list(j_vs_swift['docs']['categories']))

	def test_metadata(self):
		corpus = build_hamlet_jz_corpus()
		meta = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
			.to_dict('hamlet', metadata=meta))
		self.maxDiff = None
		j['docs']['labels'] = list(j['docs']['labels'])
		self.assertEqual(j['docs'],
		                 {'labels': [0, 0, 0, 0, 1, 1, 1, 1],
		                  'categories': ['hamlet', 'jay-z/r. kelly'],
		                  'meta': ['one',
		                           'two',
		                           'three',
		                           'four',
		                           'five',
		                           'six',
		                           'seven',
		                           'eight'],
		                  'texts': ["what art thou that usurp'st this time of night,",
		                            'together with that fair and warlike form',
		                            'in which the majesty of buried denmark',
		                            'did sometimes march? by heaven i charge thee, speak!',
		                            'halt! who goes there?',
		                            'it is i sire tone from brooklyn.',
		                            'well, speak up man what is it?',
		                            'news from the east sire! the best of both worlds has returned!']}
		                 )

	def test_alternative_text(self):
		corpus = build_hamlet_jz_corpus_with_alt_text()
		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
			.to_dict('hamlet', alternative_text_field='alt'))
		self.assertEqual(j['docs']['texts'][0], j['docs']['texts'][0].upper())

		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
			.to_dict('hamlet'))
		self.assertNotEqual(j['docs']['texts'][0], j['docs']['texts'][0].upper())

	def test_extra_features(self):
		corpus = build_hamlet_jz_corpus_with_meta()
		meta = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0,
		                          use_non_text_features=True)
			.to_dict('hamlet', metadata=meta))
		extras = [{'cat3': 1, 'cat4': 2},
		          {'cat4': 2},
		          {'cat3': 2, 'cat5': 1},
		          {'cat6': 2, 'cat9': 1},
		          {'cat3': 1, 'cat4': 2},
		          {'cat1': 2, 'cat2': 1},
		          {'cat2': 2, 'cat5': 1},
		          {'cat3': 2, 'cat4': 1}]
		extras = [{'cat1': 2}] * 8
		self.maxDiff = None
		j['docs']['labels'] = list(j['docs']['labels'])
		self.assertEqual(j['docs'],
		                 {'labels': [0, 0, 0, 0, 1, 1, 1, 1],
		                  'categories': ['hamlet', 'jay-z/r. kelly'],
		                  'extra': extras,
		                  'meta': ['one',
		                           'two',
		                           'three',
		                           'four',
		                           'five',
		                           'six',
		                           'seven',
		                           'eight'],
		                  'texts': ["what art thou that usurp'st this time of night,",
		                            'together with that fair and warlike form',
		                            'in which the majesty of buried denmark',
		                            'did sometimes march? by heaven i charge thee, speak!',
		                            'halt! who goes there?',
		                            'it is i sire tone from brooklyn.',
		                            'well, speak up man what is it?',
		                            'news from the east sire! the best of both worlds has returned!']}
		                 )
