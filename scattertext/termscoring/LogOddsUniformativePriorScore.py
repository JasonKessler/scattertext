import numpy as np

from scattertext.termsignificance import LogOddsRatioUninformativeDirichletPrior


class LogOddsUninformativePriorScore:
	@staticmethod
	def get_score(cat_word_counts, not_cat_word_counts, alpha_w=0.01):
		X = LogOddsUninformativePriorScore. \
			_turn_counts_into_matrix(cat_word_counts, not_cat_word_counts)
		p_vals = LogOddsRatioUninformativeDirichletPrior(alpha_w).get_p_vals(X)
		scores = LogOddsUninformativePriorScore._turn_pvals_into_scores(p_vals)
		return scores

	@staticmethod
	def get_delta_hats(cat_word_counts, not_cat_word_counts, alpha_w=0.01):
		return (LogOddsRatioUninformativeDirichletPrior(alpha_w)
		        .get_log_odds_with_prior(LogOddsUninformativePriorScore
		                                 ._turn_counts_into_matrix(cat_word_counts,
		                                                           not_cat_word_counts)))

	@staticmethod
	def get_delta_hats(cat_word_counts, not_cat_word_counts, alpha_w=0.01):
		return (LogOddsRatioUninformativeDirichletPrior(alpha_w)
		        .get_log_odds_with_prior(LogOddsUninformativePriorScore
		                                 ._turn_counts_into_matrix(cat_word_counts,
		                                                           not_cat_word_counts)))

	@staticmethod
	def get_thresholded_score(cat_word_counts, not_cat_word_counts,
	                          alpha_w=0.01,
	                          threshold=0.1):
		scores = (LogOddsRatioUninformativeDirichletPrior(alpha_w)
		          .get_p_values_from_counts(cat_word_counts, not_cat_word_counts)) * 2 - 1
		# scores = (np.min(np.array([1 - scores, scores]), axis=0) <= threshold) * scores
		return scores * ((scores < - (1. - (threshold * 2)))
		                 | (scores > (1. - (threshold * 2))))

	@staticmethod
	def _turn_counts_into_matrix(cat_word_counts, not_cat_word_counts):
		return np.array([cat_word_counts, not_cat_word_counts]).T

	@staticmethod
	def _turn_pvals_into_scores(p_vals):
		# return np.max(np.array([1 - p_vals, p_vals]), axis=0)
		return -((p_vals - 0.5) * 2)
