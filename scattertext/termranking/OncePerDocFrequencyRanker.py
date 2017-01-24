from scipy.sparse import csr_matrix
import numpy as np
from scattertext.termranking.TermRanker import TermRanker


class OncePerDocFrequencyRanker(TermRanker):
	def get_ranks(self):
		row = self._get_row_category_ids()
		X = self._get_X()
		normX = csr_matrix(X.astype(np.bool).astype(np.int32))
		categoryX = csr_matrix((normX.data, (row, normX.indices)))
		return self._get_freq_df(categoryX)
