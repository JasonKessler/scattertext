# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import norm

from scattertext.termsignificance.TermSignificance import TermSignificance


class LogOddsRatioUninformativeDirichletPrior(TermSignificance):
	def __init__(self, alpha_w=0.01):
		'''
		Parameters
		----------
		alpha_w : np.float
			The constant prior.
		'''
		self.alpha_w = alpha_w

	def get_p_vals(self, X):
		'''
		Implements the log-odds-ratio with an uninformative dirichlet prior from
		Monroe, B. L., Colaresi, M. P., & Quinn, K. M. (2008). Fightin' words: Lexical feature selection and evaluation for identifying the content of political conflict. Political Analysis, 16(4), 372–403.

		Parameters
		----------
		X : np.array
			Array of word counts, shape (N, 2) where N is the vocab size.  X[:,0] is the
			positive class, while X[:,1] is the negative class.

		Returns
		-------
		np.array of p-values

		'''
		a_w = self.alpha_w
		n_pos, n_neg = X.sum(axis=0)
		a_0 = X.shape[0] * a_w

		# Equation 16 of Monroe et al. 2008.
		lod_odds_ratio = (np.log((X[:, 0] + a_w) / (n_pos + a_0 - X[:, 0] - a_w))
		                  - np.log((X[:, 1] + a_w) / (n_neg + a_0 - X[:, 1] - a_w)))

		# Equation 19
		std_lod_odds_ratio = (1. / (X[:, 0] + a_w)
		                      + 1. / (n_pos + a_0 - X[:, 0] - a_w)
		                      + 1. / (X[:, 1] + a_w)
		                      + 1. / (n_neg + a_0 - X[:, 1] - a_w))

		# Equation 22
		z_scores = lod_odds_ratio / np.sqrt(std_lod_odds_ratio)

		return norm.cdf(z_scores)


