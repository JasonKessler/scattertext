import numpy as np


def filter_bigrams_by_pmis(word_freq_df, threshold_coef=2):
	if len(word_freq_df.index) == 0:
		return word_freq_df

	low_pmi_bigrams = get_low_pmi_bigrams(threshold_coef, word_freq_df)
	return word_freq_df.drop(low_pmi_bigrams.index)


def get_low_pmi_bigrams(threshold_coef, word_freq_df):
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


class TermDocMatrixFilter:
	def __init__(self, pmi_threshold_coef=2, min_freq=3):
		self._threshold_coef = pmi_threshold_coef
		self._min_freq = min_freq

	def filter(self, term_doc_matrix):
		'''
		:param term_doc_matrix: TermDocMatrix
		:return: TermDocMatrix pmi-filterd term doc matrix
		'''
		df = term_doc_matrix.get_term_freq_df()
		if len(df) == 0:
			return term_doc_matrix
		low_pmi_bigrams = get_low_pmi_bigrams(self._threshold_coef, df).index
		infrequent_terms = df[df.sum(axis=1) < self._min_freq].index
		return term_doc_matrix.remove_terms(set(low_pmi_bigrams + infrequent_terms))
