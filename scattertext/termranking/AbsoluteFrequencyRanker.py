from scattertext.termranking.TermRanker import TermRanker


class AbsoluteFrequencyRanker(TermRanker):
	'''Ranks terms by the number of times they occur in each category.

	'''
	def get_ranks(self, label_append=' freq'):
		'''
		Returns
		-------
		pd.DataFrame

		'''
		if self._use_non_text_features:
			return self._corpus.get_metadata_freq_df(label_append=label_append)
		else:
			return self._corpus.get_term_freq_df(label_append=label_append)

