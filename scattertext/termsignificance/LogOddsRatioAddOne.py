# -*- coding: utf-8 -*-
import numpy as np
from scipy.special import ndtr

from scattertext.Scalers import scale_neg_1_to_1_with_zero_mean_abs_max
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termsignificance.TermSignificance import TermSignificance


def z_to_p_val(z_scores):
	# return norm.sf(-z_scores) - 0.5 + 0.5
	return ndtr(z_scores)


class LogOddsRatioAddOne(TermSignificance):
	def __init__(self, alpha_w=1, ranker=AbsoluteFrequencyRanker):
		'''
		Parameters
		----------
		alpha_w : np.float
			The constant prior.
		'''
		self.alpha_w = alpha_w

	def get_name(self):
		return "Log-Odds-Ratio w/ Add One Smoothing"

	def get_p_vals(self, X):
		'''
		Parameters
		----------
		X : np.array
			Array of word counts, shape (N, 2) where N is the vocab size.  X[:,0] is the
			positive class, while X[:,1] is the negative class. None by default

		Returns
		-------
		np.array of p-values

		'''
		# Eqs 19-22
		return z_to_p_val(self.get_zeta_i_j(X))

	def get_p_vals_given_separate_counts(self, y_i, y_j):
		'''
		Parameters
		----------
		y_i, np.array(int)
			Arrays of word counts of words occurring in positive class
		y_j, np.array(int)

		Returns
		np.array of p-values
		'''
		return z_to_p_val(self.get_zeta_i_j_given_separate_counts(y_i, y_j))

	def get_zeta_i_j_given_separate_counts(self, y_i, y_j):
		'''
		Parameters
		----------
		y_i, np.array(int)
			Arrays of word counts of words occurring in positi ve class
		y_j, np.array(int)

		Returns
		-------
		np.array of z-scores
		'''
		n_i, n_j = y_i.sum(), y_j.sum()
		delta_i_j = (np.log((y_i + 1) / (1. + n_i - y_i))
		             - np.log((y_j + 1) / (1. + n_j - y_j)))
		return delta_i_j

	def get_zeta_i_j(self, X):
		'''
		Parameters
		----------
		X : np.array
			Array of word counts, shape (N, 2) where N is the vocab size.  X[:,0] is the
			positive class, while X[:,1] is the negative class. None by default

		Returns
		-------
		np.array of z-scores
		'''
		y_i, y_j = X.T[0], X.T[1]
		return self.get_zeta_i_j_given_separate_counts(y_i, y_j)

	def get_default_score(self):
		return 0

	def get_scores(self, y_i, y_j):
		'''
		Same function as get_zeta_i_j_given_separate_counts

		Parameters
		----------
		y_i, np.array(int)
			Arrays of word counts of words occurring in positive class
		y_j, np.array(int)

		Returns
		-------
		np.array of z-scores
		'''
		z_scores = self.get_zeta_i_j_given_separate_counts(y_i, y_j)
		#scaled_scores = scale_neg_1_to_1_with_zero_mean_abs_max(z_scores)
		return z_scores
