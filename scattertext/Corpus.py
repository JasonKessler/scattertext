import pandas as pd
from numpy import nonzero

from scattertext import TermDocMatrix


class Corpus(TermDocMatrix):
	def __init__(self, X, y, term_idx_store, category_idx_store,
	             raw_texts, unigram_frequency_path=None):
		'''
		Parameters
		----------
		X csr_matrix
		y np.array
		term_idx_store IndexStore
		category_idx_store IndexStore
		raw_texts np.array or pd.Series
		unigram_frequency_path str or None
		'''
		TermDocMatrix.__init__(self, X, y, term_idx_store,
		                       category_idx_store, unigram_frequency_path)
		self._raw_texts = raw_texts

	def get_texts(self):
		return self._raw_texts

	def search(self, ngram):
		mask = self._document_index_mask(ngram)
		return pd.DataFrame({
			'text': self._raw_texts[mask],
			'category': [self._category_idx_store.getval(idx)
			             for idx in self._y[mask]]
		})

	def search_index(self, ngram):
		return nonzero(self._document_index_mask(ngram))[0]

	def _document_index_mask(self, ngram):
		idx = self._term_idx_store.getidxstrict(ngram.lower())
		mask = (self._X[:, idx] > 0).todense().A1
		return mask
