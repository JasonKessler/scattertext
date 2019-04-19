from pprint import pprint
from unittest import TestCase

import pandas as pd

from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext import CorpusFromPandas, SemioticSquareFromAxes
from scattertext.test.test_corpusFromPandas import get_docs_categories


class TestSemioticSquareFromAxes(TestCase):
    @classmethod
    def setUp(cls):
        categories, documents = get_docs_categories()
        cls.df = pd.DataFrame({'category': categories,
                               'text': documents})
        cls.corpus = CorpusFromPandas(cls.df,
                                      'category',
                                      'text',
                                      nlp=whitespace_nlp).build()

    def test_main(self):
        terms = self.corpus.get_terms()
        axes = pd.DataFrame({'x': [len(x) for x in terms],
                             'y': [sum([ord(c) for c in x]) * 1. / len(x) for x in terms]}, index=terms)
        axes['x'] = axes['x'] - axes['x'].median()
        axes['y'] = axes['y'] - axes['y'].median()
        x_axis_label = 'len'
        y_axis_label = 'alpha'

        with self.assertRaises(AssertionError):
            SemioticSquareFromAxes(self.corpus, axes.iloc[:3], x_axis_label, y_axis_label)

        with self.assertRaises(AssertionError):
            axes2 = axes.copy()
            axes2.loc['asdjfksafjd'] = pd.Series({'x': 3, 'y': 3})
            SemioticSquareFromAxes(self.corpus, axes2, x_axis_label, y_axis_label)

        with self.assertRaises(AssertionError):
            SemioticSquareFromAxes(self.corpus, axes2[['x']], x_axis_label, y_axis_label)

        with self.assertRaises(AssertionError):
            axes2 = axes.copy()
            axes2['a'] = 1
            SemioticSquareFromAxes(self.corpus, axes2, x_axis_label, y_axis_label)

        semsq = SemioticSquareFromAxes(self.corpus, axes, x_axis_label, y_axis_label)
        self.assertEqual(semsq.get_labels(), {'a_and_b_label': 'alpha',
                                              'a_and_not_b_label': 'not-len',
                                              'a_label': 'not-len; alpha',
                                              'b_and_not_a_label': 'len',
                                              'b_label': 'len; alpha',
                                              'not_a_and_not_b_label': 'not-alpha',
                                              'not_a_label': 'len; not-alpha',
                                              'not_b_label': 'not-len; not-alpha'})
        self.assertEqual(semsq.get_axes().to_csv(), axes.to_csv())
        self.assertEqual(semsq.get_lexicons(3), {'a': ['st', 'up', 'usurp'],
                                                 'a_and_b': ['usurp', 'worlds', 'thou'],
                                                 'a_and_not_b': ['and', 'did', 'i'],
                                                 'b': ['sometimes', 'brooklyn', 'returned'],
                                                 'b_and_not_a': ['sometimes march', 'together with', 'did sometimes'],
                                                 'not_a': ['i charge', 'fair and', 'charge thee'],
                                                 'not_a_and_not_b': ['is a', 'is i', 'i charge'],
                                                 'not_b': ['is a', 'is i', 'it is']})
