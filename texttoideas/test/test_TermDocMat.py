import os
from unittest import TestCase

import pandas as pd
import numpy as np
from scipy.stats import rankdata, hmean, chi2_contingency

from texttoideas import TermDocMatrix
from texttoideas.TermDocMatrix import InvalidScalerException


class TestTermDocMat(TestCase):
	@classmethod
	def setUp(cls):
		cls.tdm = TermDocMatrix.build_from_category_whitespace_delimited_text(
			[
				['a', '''hello my name is joe.
				i've got a wife and three kids and i'm working.
				in a button factory'''],
				['b', '''this is another type of document
				 another sentence in another document
				 my name isn't joe here.'''],
				['b', '''this is another document.
					blah blah blah''']
			])

	def test_get_term_freq_df(self):
		df = self.tdm.get_term_freq_df().sort_values('b freq', ascending=False)[:3]
		self.assertEqual(list(df.index), ['another', 'blah', 'blah blah'])
		self.assertEqual(list(df['a freq']), [0, 0, 0])
		self.assertEqual(list(df['b freq']), [4, 3, 2])
		self.assertEqual(list(self.tdm.get_term_freq_df()
		                      .sort_values('a freq', ascending=False)
		                      [:3]['a freq']),
		                 [2, 2, 1])

	def test_term_scores(self):
		df = self.tdm.get_term_freq_df()
		df['posterior ratio'] = self.tdm.get_posterior_mean_ratio_scores('b')
		scores = self.tdm.get_kessler_scores('b', scaler_algo='percentile')
		df['kessler'] = np.array(scores)
		with self.assertRaises(InvalidScalerException):
			self.tdm.get_kessler_scores('a', scaler_algo='x')
		self.tdm.get_kessler_scores('a', scaler_algo='percentile')
		self.tdm.get_kessler_scores('a', scaler_algo='normcdf')
		df['rudder'] = self.tdm.get_rudder_scores('b')
		#df['fisher oddsratio'], df['fisher pval'] \
		#	= self.tdm.get_fisher_scores('b')

		self.assertEqual(list(df.sort_values(by='posterior ratio', ascending=False).index[:3]),
		                 ['another', 'blah', 'blah blah'])
		self.assertEqual(list(df.sort_values(by='kessler', ascending=False).index[:3]),
		                 ['another', 'blah', 'blah blah'])

		# to do: come up with faster way of testing fisher
		#self.assertEqual(list(df.sort_values(by='fisher pval', ascending=True).index[:3]),
		#                 ['another', 'blah', 'blah blah'])

		self.assertEqual(list(df.sort_values(by='rudder', ascending=True).index[:3]),
		                 ['another', 'blah', 'blah blah'])


	def test_term_scores_background(self):
		hamlet = self.get_hamlet()
		df = hamlet.get_kessler_scores_vs_background(
			scaler_algo='normcdf'
		)
		self.assertEqual(list(df.sort_values(by='kessler', ascending=False).index[:3]),
		                 ['hamlet', 'polonius', 'horatio'])

		df = hamlet.get_rudder_scores_vs_background()
		self.assertEqual(list(df.sort_values(by='rudder', ascending=True).index[:3]),
		                 ['voltimand', 'knavish', 'mobled'])

		df = hamlet.get_posterior_mean_ratio_scores_vs_background()
		self.assertEqual(list(df.sort_values(by='Log Posterior Mean Ratio', ascending=False).index[:3]),
		                 ['hamlet', 'horatio', 'claudius'])

		# to do: come up with faster way of testing fisher
		#df = hamlet.get_fisher_scores_vs_background()
		#self.assertEqual(list(df.sort_values(by='Bonferroni-corrected p-values', ascending=True).index[:3]),
		#                 ['voltimand', 'knavish', 'mobled'])

	def test_log_reg(self):
		hamlet = self.get_hamlet()
		df = hamlet.get_term_freq_df()
		df['logreg'], acc, baseline = hamlet.get_logistic_regression_coefs('hamlet')
		self.assertGreaterEqual(acc, 0)
		self.assertGreaterEqual(baseline, 0)
		self.assertGreaterEqual(1, acc)
		self.assertGreaterEqual(1, baseline)
		self.assertEqual(list(df.sort_values(by='logreg', ascending=False).index[:3]),
		                 ['hamlet', 'hamlet,', 'the'])

	def get_hamlet(self):
		cwd = os.path.dirname(os.path.abspath(__file__))
		path = os.path.join(cwd, '..', 'data', 'hamlet.txt')
		hamlet = TermDocMatrix.build_from_category_whitespace_delimited_text(
			[('hamlet' if 'hamlet' in text.lower() else 'not hamlet', text) for i, text in
			 enumerate(open(path).read().split('\n\n'))]
		)
		return hamlet
