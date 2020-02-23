import numpy as np

from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.indexstore import IndexStore
from scattertext.termranking import AbsoluteFrequencyRanker


class CompactTerms(object):
	def __init__(self,
	             term_ranker=AbsoluteFrequencyRanker,
	             minimum_term_count=0,
	             slack=1):
		'''

		Parameters
		----------
		term_ranker : TermRanker
			Default AbsoluteFrequencyRanker
		minimum_term_count : int
			Default 0
		slack : int
			Default 1

		'''
		self.term_ranker = term_ranker
		self.minimum_term_count = minimum_term_count
		self.redundancy_slack = slack

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

	def _indices_to_compact(self, term_doc_matrix, non_text=False):
		ranker = self.term_ranker(term_doc_matrix)
		if non_text:
			ranker = ranker.use_non_text_features()
		indicies = self._get_term_indices_to_compact_from_term_freqs(
			ranker.get_ranks(),
			term_doc_matrix,
			non_text
		)
		return list(indicies)

	def _get_term_indices_to_compact_from_term_freqs(self, term_freqs, term_doc_matrix, non_text):
		idx = IndexStore()
		tdf_vals = term_freqs.values
		valid_terms_mask = tdf_vals.sum(axis=1) >= self.minimum_term_count
		tdf_vals = term_freqs[valid_terms_mask].values
		terms = np.array(term_freqs.index)[valid_terms_mask]

		lengths = []
		fact = CSRMatrixFactory()
		for i, t in enumerate(terms):
			for tok in t.split():
				fact[i, idx.getidx(tok)] = 1
			lengths.append(len(t.split()))
		lengths = np.array(lengths)
		mat = fact.get_csr_matrix()

		coocs = lengths - (mat * mat.T)
		pairs = np.argwhere(coocs == 0).T
		pairs = self._limit_to_non_identical_terms(pairs)
		pairs = self._limit_to_pairs_of_bigrams_and_a_constituent_unigram(pairs, terms)
		pairs = self._limit_to_redundant_unigrams(pairs, tdf_vals)
		idx_store = term_doc_matrix._get_relevant_idx_store(non_text)
		redundant_terms = idx_store.getidxstrictbatch(terms[np.unique(pairs[:, 1])])
		infrequent_terms = np.argwhere(~valid_terms_mask).T[0]
		terms_to_remove = np.concatenate([redundant_terms, infrequent_terms])
		return terms_to_remove

	def _limit_to_redundant_unigrams(self, pairs, tdf_vals):
		return pairs[np.all(tdf_vals[pairs[:, 1]] <= tdf_vals[pairs[:, 0]] + self.redundancy_slack, axis=1)]

	def _limit_to_pairs_of_bigrams_and_a_constituent_unigram(self, pairs, terms):
		return pairs[np.array([terms[i[1]] in terms[i[0]] for i in pairs])]

	def _limit_to_non_identical_terms(self, pairs):
		return pairs.T[(pairs[0] != pairs[1])]
