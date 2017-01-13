from pprint import pprint
from unittest import TestCase

import numpy as np

from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestScatterChart(TestCase):
	def test_to_dict(self):
		corpus = build_hamlet_jz_corpus()
		j = (ScatterChartExplorer(corpus,
		                          minimum_term_frequency=0)
		     .to_dict('hamlet'))
		self.assertEqual(set(j.keys()), set(['info', 'data', 'docs']))
		self.assertEqual(set(j['info'].keys()),
		                 set(['not_category_name', 'category_name',
		                      'category_terms', 'not_category_terms','category_internal_name']))
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
		expected = {"x": 0.0,
		            "y": 0.42000000000000004,
		            "term": u"art",
		            "cat25k": 758,
		            "ncat25k": 0,
		            's': 0.5,
		            'os': 0.5192,
		            'cat': 1,
		            'ncat': 0,
		            # not sure if i want to do it this way
		            #'docids': [0]
		            }
		datum = j['data'][0]
		for var in expected.keys():
			try:
				np.testing.assert_almost_equal(datum[var], expected[var])
			except TypeError:
				self.assertEqual(datum[var], expected[var])
		self.assertEqual(set(expected.keys()), set(datum.keys()))
		self.assertEqual(expected['term'], datum['term'])
		self.assertEqual(j['docs'].keys(), ['texts', 'labels', 'categories'])

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


