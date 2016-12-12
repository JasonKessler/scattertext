from unittest import TestCase

import numpy as np

from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestScatterChart(TestCase):
	def test_to_dict(self):
		corpus = build_hamlet_jz_corpus()
		j = (ScatterChartExplorer(term_doc_matrix=corpus,
		                          minimum_term_frequency=0)
		     .to_dict('hamlet'))
		self.assertEqual(set(j.keys()), set(['info', 'data', 'docs']))
		self.assertEqual(set(j['info'].keys()),
		                 set(['not_category_name', 'category_name',
		                      'category_terms', 'not_category_terms']))
		self.assertEqual(list(j['docs']['labels']),
		                 [0, 0, 0, 0, 1, 1, 1, 1])
		print('XXX')
		print(list(j['docs']['texts']))
		self.assertEqual(list(j['docs']['texts']),
		                 ["what art thou that usurp'st this time of night,",
		                  'together with that fair and warlike form',
		                  'in which the majesty of buried denmark',
		                  'did sometimes march? by heaven i charge thee, speak!',
		                  'halt! who goes there?', 'it is i sire tone from brooklyn.',
		                  'well, speak up man what is it?',
		                  'news from the east sire! the best of both worlds has returned!'])
		expected = {"x": 0.0,
		            "y": 0.32558139534883723,
		            "term": u"art",
		            "cat25k": 758,
		            "ncat25k": 0,
		            's': 0.38095238095238093,
		            'cat': 1,
		            'ncat': 0,
		            # not sure if i want to do it this way
		            #'docids': [0]
		            }
		datum = j['data'][0]
		print('data')
		print(datum)
		print('expected')
		print(expected)
		for var in expected.keys():
			try:
				np.testing.assert_almost_equal(datum[var], expected[var])
			except TypeError:
				self.assertEqual(datum[var], expected[var])
		self.assertEqual(set(expected.keys()), set(datum.keys()))
		self.assertEqual(expected['term'], datum['term'])


