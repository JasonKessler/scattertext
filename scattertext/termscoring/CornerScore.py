import numpy as np
from scipy.stats import rankdata


class CornerScore(object):
	@staticmethod
	def get_scores(cat_word_counts, not_cat_word_counts):
		pos = CornerScore.get_scores_for_category(cat_word_counts, not_cat_word_counts)
		neg = CornerScore.get_scores_for_category(not_cat_word_counts, cat_word_counts)
		scores = CornerScore._balance_scores(pos, neg)
		return scores

	@staticmethod
	def _balance_scores(cat_scores, not_cat_scores):
		scores = np.zeros(len(cat_scores))
		scores[cat_scores < not_cat_scores] \
			= np.sqrt(2) - cat_scores[cat_scores < not_cat_scores]
		scores[not_cat_scores < cat_scores] \
			= -(np.sqrt(2) - not_cat_scores[not_cat_scores < cat_scores])
		return ((scores / np.sqrt(2)) + 1.) / 2

	@staticmethod
	def get_scores_for_category(cat_word_counts, not_cat_word_counts):
		cat_pctls = CornerScore._get_percentiles_from_freqs(cat_word_counts)
		not_cat_pctls = CornerScore._get_percentiles_from_freqs(not_cat_word_counts)
		return CornerScore._distance_from_upper_left(cat_pctls, not_cat_pctls)

	@staticmethod
	def _distance_from_upper_left(cat_pctls, not_cat_pctls):
		return np.linalg.norm(np.array([1, 0]) - np.array(list(zip(cat_pctls, not_cat_pctls))),
		                      axis=1)

	@staticmethod
	def _get_percentiles_from_freqs(freqs):
		return rankdata(freqs) * 1. / len(freqs)
