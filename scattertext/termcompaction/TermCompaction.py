import numpy as np

from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.indexstore import IndexStore
from scattertext.termranking import AbsoluteFrequencyRanker


class CompactTerms(object):
	def __init__(self,
	             term_doc_matrix,
	             term_ranker=AbsoluteFrequencyRanker,
	             minimum_term_count=2):
		'''

		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			Term document matrix object to compact
		term_ranker : TermRanker
			Default AbsoluteFrequencyRanker
		minimum_term_count : int
			Default 2

		'''
		self.term_doc_matrix = term_doc_matrix
		self.term_ranker = term_ranker
		self.minimum_term_count = minimum_term_count

	def compact(self):
		'''
		Returns
		-------
		New term doc matrix
		'''
		return self.term_doc_matrix.remove_terms_by_indices(self._indices_to_compact())

	def _indices_to_compact(self):
		indicies = self._get_term_indices_to_compact_from_term_freqs(
			self.term_ranker(self.term_doc_matrix).get_ranks()
		)
		return list(indicies)

	def _get_term_indices_to_compact_from_term_freqs(self, term_freqs):
		fact = CSRMatrixFactory()
		idx = IndexStore()
		tdf_vals = term_freqs.values
		valid_terms_mask = tdf_vals.sum(axis=1) >= self.minimum_term_count
		tdf_vals = term_freqs[valid_terms_mask].values
		terms = np.array(term_freqs.index)[valid_terms_mask]
		lengths = []
		for i, t in enumerate(terms):
			for tok in t.split():
				fact[i, idx.getidx(tok)] = 1
			lengths.append(len(t.split()))
		lengths = np.array(lengths)
		mat = fact.get_csr_matrix()
		coocs = lengths - (mat * mat.T)
		pairs = np.argwhere(coocs == 0).T
		pairs = pairs.T[(pairs[0] != pairs[1])]
		pairs = pairs[np.array([terms[i[1]] in terms[i[0]] for i in pairs])]
		pairs = pairs[np.all(tdf_vals[pairs[:, 1]] <= tdf_vals[pairs[:, 0]], axis=1)]
		idx_store = self.term_doc_matrix._term_idx_store
		redundant_terms = idx_store.getidxstrictbatch(terms[np.unique(pairs[:, 1])])
		infrequent_terms = np.argwhere(~valid_terms_mask).T[0]
		terms_to_remove = np.concatenate([redundant_terms, infrequent_terms])
		return terms_to_remove
