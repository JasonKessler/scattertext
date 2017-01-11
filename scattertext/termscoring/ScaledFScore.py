import numpy as np
import pandas as pd
from scipy.stats import hmean, norm, rankdata

class InvalidScalerException(Exception):
	pass

class ScaledFScore(object):
	@staticmethod
	def get_scores(cat_word_counts, not_cat_word_counts, scaler_algo='normcdf', beta=1.):
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
			np.array of harmonic means of scaled P(word|category) and scaled P(category|word)
		'''
		assert beta > 0
		scores = ScaledFScore._get_scaled_f_score_from_counts(cat_word_counts, not_cat_word_counts, scaler_algo, beta)
		return np.array(scores)

	@staticmethod
	def _get_scaled_f_score_from_counts(cat_word_counts, not_cat_word_counts, scaler_algo, beta=1):
		scaler = ScaledFScore._get_scaler_function(scaler_algo)
		p_word_given_category = cat_word_counts.astype(np.float64) / cat_word_counts.sum()
		p_category_given_word = cat_word_counts.astype(np.float64) \
		                        / (cat_word_counts + not_cat_word_counts)
		scores \
			= ScaledFScore._computer_harmoic_mean_of_probabilities_over_non_zero_in_category_count_terms \
			(cat_word_counts, p_category_given_word, p_word_given_category, scaler)
		return scores

	@staticmethod
	def _computer_harmoic_mean_of_probabilities_over_non_zero_in_category_count_terms(
			cat_word_counts,
			p_category_given_word,
			p_word_given_category,
			scaler):
		df = pd.DataFrame({
			'cat_word_counts': cat_word_counts,
			'p_word_given_category': p_word_given_category,
			'p_category_given_word': p_category_given_word
		})
		df_with_count = df[df['cat_word_counts'] > 0]
		df_with_count['scale p_word_given_category'] = scaler(df_with_count['p_word_given_category'])
		df_with_count['scale p_category_given_word'] = scaler(df_with_count['p_category_given_word'])
		df['scale p_word_given_category'] = 0
		df.loc[df_with_count.index, 'scale p_word_given_category'] \
			= df_with_count['scale p_word_given_category']
		df['scale p_category_given_word'] = 0
		df.loc[df_with_count.index, 'scale p_category_given_word'] \
			= df_with_count['scale p_category_given_word']
		score = hmean([df_with_count['scale p_category_given_word'],
		               df_with_count['scale p_word_given_category']])
		df['score'] = 0
		df.loc[df_with_count.index, 'score'] = score
		return df['score']

	@staticmethod
	def _get_scaler_function(scaler_algo):
		scaler = None
		if scaler_algo == 'percentile':
			scaler = lambda x: norm.cdf(x, x.mean(), x.std())
		elif scaler_algo == 'normcdf':
			scaler = lambda x: rankdata(x).astype(np.float64) / len(x)
		elif scaler_algo == 'none':
			scaler = lambda x: x
		else:
			raise InvalidScalerException("Invalid scaler alogrithm.  Must be either percentile or normcdf.")
		return scaler


