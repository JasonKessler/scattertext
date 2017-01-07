from collections import Counter

import numpy as np


def filter_bigrams_by_pmis(word_freq_df, threshold_coef=2):
	# type: (pd.DataFrame, int) -> pd.DataFrame
	if len(word_freq_df.index) == 0:
		return word_freq_df
	low_pmi_bigrams = get_low_pmi_bigrams(threshold_coef, word_freq_df)
	return word_freq_df.drop(low_pmi_bigrams.index)


def filter_out_unigrams_that_only_occur_in_one_bigram(df):
	# type: (pd.DataFrame) -> pd.DataFrame
	bigrams = {bigram for bigram in df.index if ' ' in bigram}
	unigrams_to_remove = unigrams_that_only_occur_in_one_bigram(bigrams)
	return df.drop(unigrams_to_remove)


def unigrams_that_only_occur_in_one_bigram(bigrams):
	# type: (set) -> set
	tok_bigram_counts = Counter()
	for bigram in bigrams:
		for tok in bigram.split():
			tok_bigram_counts[tok] += 1
	return {tok for tok, count in tok_bigram_counts.items() if count == 1}

def get_low_pmi_bigrams(threshold_coef, word_freq_df):
	# type: (float, pd.DataFrame) -> object
	is_bigram = np.array([' ' in word for word in word_freq_df.index])
	unigram_freq = word_freq_df[~is_bigram].sum(axis=1)
	bigram_freq = word_freq_df[is_bigram].sum(axis=1)
	bigram_prob = bigram_freq / bigram_freq.sum()
	unigram_prob = unigram_freq / unigram_freq.sum()

	def get_pmi(bigram):
		return np.log(
			bigram_prob[bigram] / np.product([unigram_prob[word] for word in bigram.split(' ')])
		) / np.log(2)

	low_pmi_bigrams = bigram_prob[bigram_prob.index.map(get_pmi) < threshold_coef * 2]
	return low_pmi_bigrams


class AtLeastOneCategoryHasNoTermsException(Exception):
	pass


class TermDocMatrixFilter:
	'''
	Filter out terms below a particular frequency or pmi threshold.
	'''
	def __init__(self, pmi_threshold_coef=2, minimum_term_freq=3):
		'''
		Parameters
		----------
		pmi_threshold_coef : float
			Bigram filtering threshold (2 * PMI). Default 2.
		minimum_term_freq : int
			Minimum number of itmes term has to appear.  Default 3.

		'''
		self._threshold_coef = pmi_threshold_coef
		self._min_freq = minimum_term_freq

	def filter(self, term_doc_matrix):
		'''
		Parameters
		----------
		term_doc_matrix  : TermDocMatrix

		Returns
		-------
		TermDocMatrix pmi-filterd term doc matrix
		'''
		df = term_doc_matrix.get_term_freq_df()
		if len(df) == 0:
			return term_doc_matrix
		low_pmi_bigrams = get_low_pmi_bigrams(self._threshold_coef, df).index
		infrequent_terms = df[df.sum(axis=1) < self._min_freq].index
		filtered_term_doc_mat = term_doc_matrix.remove_terms(set(low_pmi_bigrams | infrequent_terms))
		try:
			filtered_term_doc_mat.get_term_freq_df()
		except ValueError:
			raise AtLeastOneCategoryHasNoTermsException()
		return filtered_term_doc_mat
