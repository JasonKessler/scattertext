from abc import ABCMeta, abstractmethod


class TermRanker:
	__metaclass__ = ABCMeta

	def __init__(self, term_doc_matrix):
		'''Initialize TermRanker

		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			TermDocMatrix from which to find term ranks.
		'''
		self._term_doc_matrix = term_doc_matrix
		self._use_non_text_features = False

	def use_non_text_features(self):
		'''
		Returns
		-------
		None

		Side Effect
		-------
		Use use_non_text_features instead of text
		'''
		self._use_non_text_features = True

	def get_X(self):
		'''
		:return: term freq matrix or metadata freq matrix
		'''
		if self._use_non_text_features:
			return self._term_doc_matrix._mX
		else:
			return self._term_doc_matrix._X

	def _get_freq_df(self, X):
		if self._use_non_text_features:
			return self._term_doc_matrix._metadata_freq_df_from_matrix(X)
		else:
			return self._term_doc_matrix._term_freq_df_from_matrix(X)

	def _get_row_category_ids(self):
		if self._use_non_text_features:
			return self._term_doc_matrix._row_category_ids_for_meta()
		else:
			return self._term_doc_matrix._row_category_ids()


	@abstractmethod
	def get_ranks(self):
		pass