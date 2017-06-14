import random
from unittest import TestCase

import numpy as np

from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus, build_hamlet_jz_corpus_with_meta


class TestScatterChart(TestCase):
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
		                      'category_terms', 'not_category_terms', 'category_internal_name']))
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
		            'cat': 1, 's': 0.5, 'term': 'art', 'os': 0.5192,
		            'cat25k': 758, 'x': 0.06}

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

	def test_metadata(self):
		corpus = build_hamlet_jz_corpus()
		meta = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
		     .to_dict('hamlet', metadata=meta))
		self.maxDiff = None
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
