# -*- coding: utf-8 -*-
import numpy as np

from scattertext.Common import DEFAULT_SCALER_ALGO, DEFAULT_BETA
from scattertext.termscoring import ScaledFScore
from scipy.stats import norm

from scattertext.termsignificance.TermSignificance import TermSignificance


class ScaledFScoreSignificance(TermSignificance):
	def __init__(self, scaler_algo = DEFAULT_SCALER_ALGO, beta=DEFAULT_BETA):
		'''
		Parameters
		----------
		scaler_algo : str
			Function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'. Default normcdf.
		beta : float
			Beta in (1+B^2) * (Scale(P(w|c)) * Scale(P(c|w)))/(B^2*Scale(P(w|c)) + Scale(P(c|w))). Defaults to 1.
		'''
		self.scaler_algo = scaler_algo
		self.beta = beta

	def get_p_vals(self, X):
		'''
		Imputes p-values from the Z-scores of `ScaledFScore` scores.  Assuming incorrectly
		that the scaled f-scores are normally distributed.

		Parameters
		----------
		X : np.array
			Array of word counts, shape (N, 2) where N is the vocab size.  X[:,0] is the
			positive class, while X[:,1] is the negative class.

		Returns
		-------
		np.array of p-values

		'''
		f_scores = ScaledFScore.get_scores(X[:,0], X[:,1], self.scaler_algo, self.beta)
		z_scores = (f_scores - np.mean(f_scores))/(np.std(f_scores)/np.sqrt(len(f_scores)))
		return norm.cdf(z_scores)


