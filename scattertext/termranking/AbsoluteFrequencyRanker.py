from scattertext.termranking.TermRanker import TermRanker


class AbsoluteFrequencyRanker(TermRanker):
	'''Ranks terms by the number of times they occur in each category.

	'''
	def get_ranks(self):
		'''
		Returns
		-------
		pd.DataFrame

		'''
		return self._term_doc_matrix.get_term_freq_df()
