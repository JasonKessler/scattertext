import numpy as np

from scattertext.termranking import AbsoluteFrequencyRanker


class ClassPercentageCompactor(object):
	def __init__(self,
	             term_ranker=AbsoluteFrequencyRanker,
	             term_count=2):
		'''
		Limit terms to ones that make up a minimum percentage
		of documents in a category.  Given a term_count, set the threshold
		to that of the smallest class.

		Parameters
		----------
		term_ranker : TermRanker
		term_count : int
		'''
		self.term_ranker = term_ranker
		self.term_count = term_count

	def compact(self, term_doc_matrix, non_text=False):
		'''
		Parameters
		-------
		term_doc_matrix : TermDocMatrix
		non_text : bool

		Returnss
		-------
		New term doc matrix
		'''
		ranker = self.term_ranker(term_doc_matrix)
		if non_text:
			ranker = ranker.use_non_text_features()
		tdf = ranker.get_ranks()
		tdf_sum = tdf.sum(axis=0)
		tdf_portions = tdf / tdf_sum
		threshold = np.max(self.term_count / tdf_sum)
		terms_to_remove = tdf_portions[~(tdf_portions > threshold).any(axis=1)].index
		return term_doc_matrix.remove_terms(terms_to_remove, non_text=non_text)

