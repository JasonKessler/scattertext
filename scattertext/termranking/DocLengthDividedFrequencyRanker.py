from scipy.sparse import csr_matrix
import numpy as np
from scattertext.termranking.DocLengthNormalizedFrequencyRanker import DocLengthNormalizedFrequencyRanker


class DocLengthDividedFrequencyRanker(DocLengthNormalizedFrequencyRanker):
	def _get_normalized_X(self, X, doc_lengths):
		return csr_matrix(X.astype(np.float32) / doc_lengths)
