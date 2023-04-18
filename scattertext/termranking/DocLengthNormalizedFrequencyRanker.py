import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from scattertext.termranking.TermRanker import TermRanker


class DocLengthNormalizedFrequencyRanker(TermRanker):
	'''Ranks terms by their document-length adjusted frequency instead of their raw frequency.
	This means that each term has a document-specific weight of  #(t,d)/|d|.
	'''

	def get_ranks(self,label_append: str=' freq') -> pd.DataFrame:
		X = self.get_term_doc_mat()
		y = self._corpus.get_category_ids()
		doc_lengths = X.sum(axis=1)
		norm_x = np.nan_to_num(X / doc_lengths, 0)
		data = {}
		for i in set(y):
			cat = self._corpus.get_category_index_store().getval(i)
			data[cat + label_append] = norm_x[y == i, :].sum(axis=0).A1
		return pd.DataFrame(data, index=self._corpus.get_terms(use_metadata=self._use_non_text_features))


"""
class VarianceSensitiveFrequencyRanker(TermRanker):
	'''Rank terms by their mean document frequency divided by the standard errors.'''

	def get_ranks(self, label_append=' freq'):
		X = self.get_X()
		d = {}
		y = self._term_doc_matrix._y
		for idx, cat in self._term_doc_matrix._category_idx_store.items():
			catX = X[y == idx, :]
			catXB = (catX > 0).astype(np.float64)
			means = catX.mean(axis=0)
			non_zero_sds_numerators = ((catX - catXB.multiply(csr_matrix(means)))
			                           .power(2).sum(axis=0))
			zero_dfs_numerators = ((catX.shape[0] - catX.getnnz(axis=0))
			                       * np.power(means, 2).A1)
			ses = (np.sqrt(non_zero_sds_numerators + zero_dfs_numerators
			               / (catX.shape[0] - 1))) / np.sqrt(catX.shape[0])
			return means/ses
"""

