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

	def __init__(self,
	             priors,
	             sigma=10,
	             scale_type='none',
	             prior_power=1):
		'''
		Parameters
		----------
		priors : pd.Series
			term -> prior count

		sigma : np.float
			prior scale

		scale_type : str
			'none': Don't scale prior. Jurafsky approach.
			'class-size': Scale prior st the sum of the priors is the same as the word count
			  in the document-class being scaled
			'corpus-size': Scale prior to the size of the corpus
			'word': Original formulation from MCQ. Sum of priors will be sigma.
			'background-corpus-size': Scale corpus size to multiple of background-corpus.

		prior_power : numeric
			Exponent to apply to prior
			> 1 will shrink frequent words

		'''
		assert scale_type in ['none', 'class-size', 'corpus-size',
		                      'background-corpus-size', 'word']
		self._priors = priors
		self._scale_type = scale_type
		self._prior_power = prior_power
		self._scale = sigma
		LogOddsRatioUninformativeDirichletPrior.__init__(self, sigma)

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
		n_i, n_j = y_i.sum(), y_j.sum()
		prior_scale_j = prior_scale_i = 1
		if self._scale_type == 'class-size':
			prior_scale_i = ((n_i) * self._scale * 1. / np.sum(self._priors))
			prior_scale_j = ((n_j) * self._scale * 1. / np.sum(self._priors))
		elif self._scale_type == 'corpus-size':
			prior_scale_j = prior_scale_i = ((n_i + n_j) * self._scale * 1. / np.sum(self._priors))
		elif self._scale_type == 'word':
			prior_scale_j = prior_scale_i = self._scale / np.sum(self._priors)
		elif self._scale_type == 'background-corpus-size':
			prior_scale_j = prior_scale_i = self._scale
		a_wj = (self._priors * prior_scale_j) ** self._prior_power
		a_0j = np.sum(a_wj)
		a_wi = (self._priors * prior_scale_i) ** self._prior_power
		a_0i = np.sum(a_wi)

		delta_i_j = (np.log((y_i + a_wi) / (n_i + a_0i - y_i - a_wi))
		             - np.log((y_j + a_wj) / (n_j + a_0j - y_j - a_wj)))
		var_delta_i_j = (1. / (y_i + a_wi)
		                 + 1. / (n_i + a_0i - y_i - a_wi)
		                 + 1. / (y_j + a_wj)
		                 + 1. / (n_j + a_0j - y_j - a_wj))
		zeta_i_j = delta_i_j / np.sqrt(var_delta_i_j)
		return zeta_i_j
