import numpy as np
import pandas as pd


class PhraseSelector(object):
	def __init__(self,
	             minimum_pmi=16):
		'''
		Filter n-grams using PMI.

		Parameters
		----------
		alpha : float
		labmda_ : "cressie_read"
			See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.power_divergence.html for
			options.
		'''
		self.minimum_pmi = minimum_pmi

	def compact(self, term_doc_matrix):
		'''
		Parameters
		-------
		term_doc_matrix : TermDocMatrix

		Returns
		-------

		New term doc matrix
		'''
		count_df = self._get_statistics_dataframe(term_doc_matrix)

		return term_doc_matrix.remove_terms(
			count_df[count_df['pmi'] < self.minimum_pmi].index
		)

	def _get_statistics_dataframe(self, term_doc_matrix):
		tdf = term_doc_matrix.get_term_freq_df().sum(axis=1)
		gram_df = pd.Series(tdf.index).apply(lambda x: pd.Series(list(reversed(x.split()))))
		gram_df['c'] = tdf.values
		gram_df['term'] = tdf.index
		gram_df = gram_df.set_index('term')
		unigram_df = gram_df[gram_df[1].isnull()][['c']]
		ngram_df = gram_df.dropna()
		count_df = pd.merge(pd.merge(ngram_df, unigram_df,
		                             left_on=0, right_index=True, suffixes=('', '0')),
		                    unigram_df, left_on=1, right_index=True, suffixes=('', '1'))
		p0 = count_df['c0'] / unigram_df['c'].sum()
		p1 = count_df['c1'] / unigram_df['c'].sum()
		p = count_df['c'] / ngram_df['c'].sum()
		count_df['pmi'] = np.log(p / (p0 * p1)) / np.log(2)
		return count_df
