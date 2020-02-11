from unittest import TestCase
import numpy as np

import pandas as pd

from scattertext.ScatterChartData import ScatterChartData
from scattertext.TermCategoryFrequencies import TermCategoryFrequencies


class TestTermCategoryFrequencies(TestCase):
	def setUp(self):
		df = pd.DataFrame(
			{'democrat': {'ago': 82, 'builds on': 1, 'filled': 3, 've got': 15, 'of natural': 2, 'and forged': 1,
			              'have built': 2, 's army': 4, 's protected': 1, 'the most': 28, 'gas alone': 1, 'you what': 9,
			              'few years': 8, 'gut education': 1, 's left': 2, 'for most': 1, 'raise': 18, 'problem can': 1,
			              'we the': 5, 'change will': 2},
			 'republican': {'ago': 39, 'builds on': 0, 'filled': 5, 've got': 16, 'of natural': 0, 'and forged': 0,
			                'have built': 1, 's army': 0, 's protected': 0, 'the most': 23, 'gas alone': 0,
			                'you what': 8, 'few years': 13, 'gut education': 0, 's left': 1, 'for most': 2, 'raise': 11,
			                'problem can': 0, 'we the': 5, 'change will': 0}}
		)
		self.term_cat_freq = TermCategoryFrequencies(df)

	def test_get_num_terms(self):
		self.assertEqual(self.term_cat_freq.get_num_terms(), 20)

	def test_get_categories(self):
		self.assertEqual(self.term_cat_freq.get_categories(), ['democrat', 'republican'])

	def test_get_scaled_f_scores_vs_background(self):
		df = self.term_cat_freq.get_scaled_f_scores_vs_background()
		self.assertGreater(len(df), 20)
		self.assertEqual(sum(df.corpus > 0), 3)
		self.assertEqual(set(df.columns), {'corpus', 'background', 'Scaled f-score'})

	def test_get_term_and_background_counts(self):
		df = self.term_cat_freq.get_term_and_background_counts()
		self.assertGreater(len(df), 20)
		self.assertEqual(sum(df.corpus > 0), 3)
		self.assertEqual(set(df.columns), {'corpus', 'background'})

	def test_get_term_category_frequencies(self):
		df = self.term_cat_freq.get_term_category_frequencies(ScatterChartData())
		self.assertEqual(len(df), self.term_cat_freq.get_num_terms())
		self.assertEqual(set(df.columns), {'democrat freq', 'republican freq'})
		self.assertEqual(df.index.name, 'term')

	def test_docs(self):
		df = pd.DataFrame(
			{'democrat': {'ago': 82, 'builds on': 1, 'filled': 3, 've got': 15, 'of natural': 2, 'and forged': 1,
			              'have built': 2, 's army': 4, 's protected': 1, 'the most': 28, 'gas alone': 1, 'you what': 9,
			              'few years': 8, 'gut education': 1, 's left': 2, 'for most': 1, 'raise': 18, 'problem can': 1,
			              'we the': 5, 'change will': 2},
			 'republican': {'ago': 39, 'builds on': 0, 'filled': 5, 've got': 16, 'of natural': 0, 'and forged': 0,
			                'have built': 1, 's army': 0, 's protected': 0, 'the most': 23, 'gas alone': 0,
			                'you what': 8, 'few years': 13, 'gut education': 0, 's left': 1, 'for most': 2, 'raise': 11,
			                'problem can': 0, 'we the': 5, 'change will': 0}}
		)
		doc_df = pd.DataFrame({'text': ['Blah blah gut education ve got filled ago',
		                                'builds on most natural gas alone you what blah',
		                                "change will 's army the most"],
		                       'category': ['republican', 'republican', 'democrat']})
		with self.assertRaises(AssertionError):
			TermCategoryFrequencies(df, doc_df.rename(columns={'text': 'te'}))
		with self.assertRaises(AssertionError):
			TermCategoryFrequencies(df, doc_df.rename(columns={'category': 'te'}))
		term_cat_freq = TermCategoryFrequencies(df, doc_df)
		np.testing.assert_array_equal(term_cat_freq.get_doc_indices(),
		                                 [term_cat_freq.get_categories().index('republican'),
		                                  term_cat_freq.get_categories().index('republican'),
		                                  term_cat_freq.get_categories().index('democrat')])
		np.testing.assert_array_equal(term_cat_freq.get_texts(),
		                                 ['Blah blah gut education ve got filled ago',
		                                  'builds on most natural gas alone you what blah',
		                                  "change will 's army the most"])

	def test_no_docs(self):
		np.testing.assert_array_equal(self.term_cat_freq.get_doc_indices(),
		                                 [])
		np.testing.assert_array_equal(self.term_cat_freq.get_texts(),
		                                 [])
