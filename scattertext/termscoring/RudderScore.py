import numpy as np
from scipy.stats import rankdata


class RudderScore(object):
	@staticmethod
	def get_score(cat_word_counts, not_cat_word_counts):
		cat_pctls = RudderScore._get_percentiles_from_freqs(cat_word_counts)
		not_cat_pctls = RudderScore._get_percentiles_from_freqs(not_cat_word_counts)
		return RudderScore._distance_from_upper_left(cat_pctls, not_cat_pctls)

	@staticmethod
	def _distance_from_upper_left(cat_pctls, not_cat_pctls):
		return np.linalg.norm(np.array([1, 0]) - np.array(list(zip(cat_pctls, not_cat_pctls))),
		                      axis=1)

	@staticmethod
	def _get_percentiles_from_freqs(freqs):
		return rankdata(freqs) / len(freqs)

