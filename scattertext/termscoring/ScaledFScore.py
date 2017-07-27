import numpy as np
from scipy.stats import norm, rankdata

from scattertext.Common import DEFAULT_SCALER_ALGO, DEFAULT_BETA


class InvalidScalerException(Exception):
	pass


class ScoreBalancer(object):
	@staticmethod
	def balance_scores(cat_scores, not_cat_scores):
		scores = ScoreBalancer.balance_scores_and_dont_scale(cat_scores, not_cat_scores)
		return ScoreBalancer._zero_centered_scale(scores)

	@staticmethod
	def balance_scores_and_dont_scale(cat_scores, not_cat_scores):
		'''
		median = np.median(cat_scores)
		scores = np.zeros(len(cat_scores)).astype(np.float)
		scores[cat_scores > median] = cat_scores[cat_scores > median]
		not_cat_mask = cat_scores < median if median != 0 else cat_scores <= median
		scores[not_cat_mask] = -not_cat_scores[not_cat_mask]
		'''
		scores = np.zeros(len(cat_scores)).astype(np.float)
		scores[cat_scores > not_cat_scores] = cat_scores[cat_scores > not_cat_scores]
		scores[cat_scores < not_cat_scores] = -not_cat_scores[cat_scores < not_cat_scores]
		return scores

	@staticmethod
	def _zero_centered_scale(ar):
		ar[ar > 0] = ScoreBalancer._scale(ar[ar > 0])
		ar[ar < 0] = -ScoreBalancer._scale(-ar[ar < 0])
		return (ar + 1) / 2.

	@staticmethod
	def _scale(ar):
		if len(ar) == 0:
			return ar
		if ar.min() == ar.max():
			return np.full(len(ar), 0.5)
		return (ar - ar.min()) / (ar.max() - ar.min())


class ScaledFScore(object):
	@staticmethod
	def get_scores(cat_word_counts, not_cat_word_counts,
	               scaler_algo=DEFAULT_SCALER_ALGO, beta=DEFAULT_BETA):
		''' Computes scaled-fscores
		Parameters
		----------
		category : str
			category name to score
		scaler_algo : str
			Function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'. Default.
		beta : float
			Beta in (1+B^2) * (Scale(P(w|c)) * Scale(P(c|w)))/(B^2*Scale(P(w|c)) + Scale(P(c|w))). Default.
		Returns
		-------
			np.array of harmonic means of scaled P(word|category)
			 and scaled P(category|word) for >median half of scores.  Low scores are harmonic means
			 of scaled P(word|~category) and scaled P(~category|word).  Array is squashed to between
			 0 and 1, with 0.5 indicating a median score.
		'''

		cat_scores = ScaledFScore.get_scores_for_category(cat_word_counts, not_cat_word_counts, scaler_algo, beta)
		not_cat_scores = ScaledFScore.get_scores_for_category(not_cat_word_counts, cat_word_counts,
		                                                      scaler_algo, beta)
		return ScoreBalancer.balance_scores(cat_scores, not_cat_scores)

	@staticmethod
	def get_scores_for_category(cat_word_counts, not_cat_word_counts,
	                            scaler_algo=DEFAULT_SCALER_ALGO, beta=DEFAULT_BETA):
		''' Computes scaled-fscores
		Parameters
		----------
		category : str
			category name to score
		scaler_algo : str
			Function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'. Default normcdf
		beta : float
			Beta in (1+B^2) * (Scale(P(w|c)) * Scale(P(c|w)))/(B^2*Scale(P(w|c)) + Scale(P(c|w))). Defaults to 1.
		Returns
		-------
			np.array of harmonic means of scaled P(word|category) and scaled P(category|word).
		'''
		assert beta > 0
		precision = (cat_word_counts * 1. / (cat_word_counts + not_cat_word_counts))
		recall = cat_word_counts * 1. / cat_word_counts.sum()
		precision_normcdf = ScaledFScore._safe_scaler(scaler_algo, precision)
		recall_normcdf = ScaledFScore._safe_scaler(scaler_algo, recall)
		scores = (1 + beta ** 2) * (precision_normcdf * recall_normcdf) \
		       / ((beta ** 2) * precision_normcdf + recall_normcdf)
		scores[np.isnan(scores)] = 0.
		return scores

	@staticmethod
	def _get_scaled_f_score_from_counts(cat_word_counts, not_cat_word_counts, scaler_algo, beta=DEFAULT_BETA):
		p_word_given_category = cat_word_counts.astype(np.float) / cat_word_counts.sum()
		p_category_given_word = cat_word_counts * 1. / (cat_word_counts + not_cat_word_counts)
		scores \
			= ScaledFScore._get_harmonic_mean_of_probabilities_over_non_zero_in_category_count_terms \
			(cat_word_counts, p_category_given_word, p_word_given_category, scaler_algo, beta)
		return scores

	@staticmethod
	def _safe_scaler(algo, ar):
		if algo == 'none':
			return ar
		scaled_ar = ScaledFScore._get_scaler_function(algo)(ar)
		if np.isnan(scaled_ar).any():
			return ScaledFScore._get_scaler_function('percentile')(scaled_ar)
		return scaled_ar

	@staticmethod
	def _get_scaler_function(scaler_algo):
		scaler = None
		if scaler_algo == 'normcdf':
			scaler = lambda x: norm.cdf(x, x.mean(), x.std())
		elif scaler_algo == 'percentile':
			scaler = lambda x: rankdata(x).astype(np.float64) / len(x)
		elif scaler_algo == 'none':
			scaler = lambda x: x
		else:
			raise InvalidScalerException("Invalid scaler alogrithm.  Must be either percentile or normcdf.")
		return scaler
