
class AutoTermSelector(object):
	'''
	Reduce corpus to the X most important terms.  Great for plotting a big corpus.
	Will return between X/2 and X terms.

	Returns the terms with the X highest absolute scores, background corpus scores, and term frequencies.
	'''

	@staticmethod
	def reduce_terms(term_doc_matrix, scores, num_term_to_keep=None):
		'''
		Parameters
		----------
		term_doc_matrix: TermDocMatrix or descendant
		scores: array-like
			Same length as number of terms in TermDocMatrix.
		num_term_to_keep: int, default=4000.
			Should be> 0. Number of terms to keep. Will keep between num_terms_to_keep/2 and num_terms_to_keep.

		Returns
		-------
		TermDocMatrix stripped of non-important terms., array of scores
		'''
		terms_to_show = AutoTermSelector.get_selected_terms(
			term_doc_matrix, scores, num_term_to_keep)
		return term_doc_matrix.remove_terms(set(term_doc_matrix.get_terms())
		                                    - set(terms_to_show))

	@staticmethod
	def get_selected_terms(term_doc_matrix, scores, num_term_to_keep=None):
		'''
		Parameters
		----------
		term_doc_matrix: TermDocMatrix or descendant
		scores: array-like
			Same length as number of terms in TermDocMatrix.
		num_term_to_keep: int, default=4000.
			Should be> 0. Number of terms to keep. Will keep between num_terms_to_keep/2 and num_terms_to_keep.

		Returns
		-------
		set, terms that should be shown
		'''
		num_term_to_keep = AutoTermSelector._add_default_num_terms_to_keep(num_term_to_keep)
		term_doc_freq = term_doc_matrix.get_term_freq_df()
		term_doc_freq['count'] = term_doc_freq.sum(axis=1)
		term_doc_freq['score'] = scores
		score_terms = AutoTermSelector._get_score_terms(num_term_to_keep, term_doc_freq)
		background_terms = AutoTermSelector._get_background_terms(num_term_to_keep, term_doc_matrix)
		frequent_terms = AutoTermSelector._get_frequent_terms(num_term_to_keep, term_doc_freq)
		terms_to_show = score_terms | background_terms | frequent_terms
		return terms_to_show

	@staticmethod
	def _get_frequent_terms(num_term_to_keep, term_doc_freq):
		return (term_doc_freq
		        .sort_values(by='count', ascending=False)
		        .iloc[:int(0.125 * num_term_to_keep)].index)

	@staticmethod
	def _get_background_terms(num_term_to_keep, term_doc_matrix):
		return (term_doc_matrix.get_scaled_f_scores_vs_background()
		        .iloc[:int(0.375 * num_term_to_keep)].index)

	@staticmethod
	def _get_score_terms(num_term_to_keep, term_doc_freq):
		sorted_tdf = term_doc_freq.sort_values(by='score', ascending=False)
		return (sorted_tdf.iloc[:int(0.25 * num_term_to_keep)].index
		        | sorted_tdf.iloc[-int(0.25 * num_term_to_keep):].index)

	@staticmethod
	def _add_default_num_terms_to_keep(num_term_to_keep):
		if num_term_to_keep is None:
			num_term_to_keep = 4000
		return num_term_to_keep

