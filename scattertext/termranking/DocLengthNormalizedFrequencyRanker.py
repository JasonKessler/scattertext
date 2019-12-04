import numpy as np
from scipy.sparse import csr_matrix

from scattertext.termranking.TermRanker import TermRanker


class DocLengthNormalizedFrequencyRanker(TermRanker):
	'''Ranks terms by their document-length adjusted frequency instead of their raw frequency.
	This means that each term has a document-specific weight of  #(t,d)/|d|.
	'''

	def get_ranks(self,label_append=' freq'):
		row = self._get_row_category_ids()
		X = self.get_X()
		return self.get_ranks_from_mat(X, row, label_append)

	def get_ranks_from_mat(self, X, row, label_append=' freq'):
		doc_lengths = X.sum(axis=1)
		normX = self._get_normalized_X(X, doc_lengths)
		categoryX = csr_matrix((normX.data, (row, normX.indices)))
		return self._get_freq_df(categoryX, label_append=label_append)

	def _get_normalized_X(self, X, doc_lengths):
		return csr_matrix(doc_lengths.mean() * X.astype(np.float32) / doc_lengths)


"""
class VarianceSensitiveFrequencyRanker(TermRanker):
	'''Rank terms by their mean document frequency divided by the standard errors.'''

	def get_ranks(self, label_append=' freq'):
		X = self.get_X()
		d = {}
		y = self._term_doc_matrix._y
		for idx, cat in self._term_doc_matrix._category_idx_store.items():
			catX = X[y == idx, :]
			catXB = (catX > 0).astype(np.float)
			means = catX.mean(axis=0)
			non_zero_sds_numerators = ((catX - catXB.multiply(csr_matrix(means)))
			                           .power(2).sum(axis=0))
			zero_dfs_numerators = ((catX.shape[0] - catX.getnnz(axis=0))
			                       * np.power(means, 2).A1)
			ses = (np.sqrt(non_zero_sds_numerators + zero_dfs_numerators
			               / (catX.shape[0] - 1))) / np.sqrt(catX.shape[0])
			return means/ses
"""

