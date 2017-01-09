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

	@abstractmethod
	def get_ranks(self): pass