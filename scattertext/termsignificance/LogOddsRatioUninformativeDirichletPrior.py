# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import norm
from scipy.special import ndtr

from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termsignificance.TermSignificance import TermSignificance


def z_to_p_val(z_scores):
	#return norm.sf(-z_scores) - 0.5 + 0.5
	return ndtr(z_scores)

class LogOddsRatioUninformativeDirichletPrior(TermSignificance):
	'''
	Implements the log-odds-ratio with an uninformative dirichlet prior from
		Monroe, B. L., Colaresi, M. P., & Quinn, K. M. (2008). Fightin' words: Lexical feature selection and evaluation for identifying the content of political conflict. Political Analysis, 16(4), 372–403.
	'''

	def __init__(self, alpha_w=0.01, ranker=AbsoluteFrequencyRanker):
		'''
		Parameters
		----------
		alpha_w : np.float
			The constant prior.
		'''
		self.alpha_w = alpha_w

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
			Arrays of word counts of words occurring in positive class
		y_j, np.array(int)

		Returns
		-------
		np.array of z-scores
		'''
		a_w = self.alpha_w
		n_i, n_j = y_i.sum(), y_j.sum()
		a_0 = len(y_i) * a_w
		delta_i_j = (np.log((y_i + a_w) / (n_i + a_0 - y_i - a_w))
		             - np.log((y_j + a_w) / (n_j + a_0 - y_j - a_w)))
		var_delta_i_j = (1. / (y_i + a_w) + 1. / (y_i + a_0 - y_i - a_w)
		                 + 1. / (y_j + a_w) + 1. / (n_j + a_0 - n_j - a_w))
		zeta_i_j = delta_i_j / np.sqrt(var_delta_i_j)
		return zeta_i_j

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

