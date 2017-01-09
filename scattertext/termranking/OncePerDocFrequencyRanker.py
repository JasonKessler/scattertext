from scipy.sparse import csr_matrix
import numpy as np
from scattertext.termranking.TermRanker import TermRanker


class OncePerDocFrequencyRanker(TermRanker):
	def get_ranks(self):
		row = self._term_doc_matrix._row_category_ids()
		normX = csr_matrix(self._term_doc_matrix._X.astype(np.bool).astype(np.int32))
		categoryX = csr_matrix((normX.data, (row, normX.indices)))
		return self._term_doc_matrix._term_freq_df_from_matrix(categoryX)
