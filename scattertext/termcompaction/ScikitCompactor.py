from sklearn.pipeline import Pipeline

class ScikitSupervisedCompactor(object):
	def __init__(self, pipeline):
		'''

		Parameters
		----------
		pipeline : Pipeline
			sklearn.pipeline.Pipeline instance
		'''
		self.pipeline = pipeline

	def compact(self, term_doc_matrix, non_text=False):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			Term document matrix object to compact
		non_text : bool
			Use non-text features instead of terms

		Returns
		-------
		New term doc matrix
		'''
		return term_doc_matrix.remove_terms_by_indices(self._indices_to_compact(term_doc_matrix, non_text), non_text)