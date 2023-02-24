from abc import ABCMeta, abstractmethod

from scattertext.TermDocMatrix import TermDocMatrix


class TermRanker:
	__metaclass__ = ABCMeta

	def __init__(self, term_doc_matrix: TermDocMatrix):
		'''Initialize TermRanker

		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			TermDocMatrix from which to find term ranks.
		'''
		self._term_doc_matrix = term_doc_matrix
		self._use_non_text_features = False

	def set_non_text(self, non_text: bool = False):
		self._use_non_text_features = non_text
		return self

	def use_non_text_features(self):
		'''
		Returns
		-------
		TermRanker

		Side Effect
		-------
		Use use_non_text_features instead of text
		'''
		self._use_non_text_features = True
		return self

	def are_non_text_features_in_use(self):
		return self._use_non_text_features

	def get_X(self):
		'''
		:return: term freq matrix or metadata freq matrix
		'''
		if self._use_non_text_features:
			return self._term_doc_matrix._mX
		else:
			return self._term_doc_matrix._X

	def _get_freq_df(self, X, label_append=' freq'):
		if self._use_non_text_features:
			return self._term_doc_matrix._metadata_freq_df_from_matrix(X, label_append=label_append)
		else:
			return self._term_doc_matrix._term_freq_df_from_matrix(X, label_append=label_append)

	def _get_row_category_ids(self):
		if self._use_non_text_features:
			return self._term_doc_matrix._row_category_ids_for_meta()
		else:
			return self._term_doc_matrix._row_category_ids()


	@abstractmethod
	def get_ranks(self, label_append = ' freq'):
		pass