# -*- coding: utf-8 -*-
import numpy as np
from scipy.special import ndtr

from scattertext.termsignificance import LogOddsRatioUninformativeDirichletPrior


def z_to_p_val(z_scores):
	# return norm.sf(-z_scores) - 0.5 + 0.5
	return ndtr(z_scores)


class LogOddsRatioInformativeDirichletPrior(LogOddsRatioUninformativeDirichletPrior):
	'''
	Implements the log-odds-ratio with an uninformative dirichlet prior from
		Monroe, B. L., Colaresi, M. P., & Quinn, K. M. (2008). Fightin' words: Lexical feature selection and evaluation for identifying the content of political conflict. Political Analysis, 16(4), 372–403.
	'''

	def __init__(self, priors, alpha_w=10):
		'''
		Parameters
		----------
		alpha_w : np.float
			The constant prior.
		'''
		self._priors = priors
		LogOddsRatioUninformativeDirichletPrior.__init__(self, alpha_w)

	def get_priors(self):
		return self._priors

	def get_name(self):
		return "Log-Odds-Ratio w/ Informative Prior"

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
		# a_w = self.alpha_w
		# prior_coef = 10
		n_i, n_j = y_i.sum(), y_j.sum()
		prior_scale_i = ((n_i) * self.alpha_w * 1. / np.sum(self._priors))
		# prior_scale_i = (self.alpha_w * 1. / np.sum(self._priors))
		a_wi = self._priors * prior_scale_i
		a_0i = np.sum(a_wi)

		prior_scale_j = ((n_j) * self.alpha_w * 1. / np.sum(self._priors))
		# prior_scale_j = (self.alpha_w * 1. / np.sum(self._priors))
		a_wj = self._priors * prior_scale_j
		a_0j = np.sum(a_wj)
		# a_0 = len(y_i) * a_w

		delta_i_j = (np.log((y_i + a_wi) / (n_i + a_0i - y_i - a_wi))
		             - np.log((y_j + a_wj) / (n_j + a_0j - y_j - a_wj)))
		var_delta_i_j = (1. / (y_i + a_wi)
		                 + 1. / (n_i + a_0i - y_i - a_wi)
		                 + 1. / (y_j + a_wj)
		                 + 1. / (n_j + a_0j - y_j - a_wj))
		zeta_i_j = delta_i_j / np.sqrt(var_delta_i_j)
		return zeta_i_j
