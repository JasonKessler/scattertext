import pandas as pd
from numpy import nonzero

from scattertext.TermDocMatrix import TermDocMatrix


class Corpus(TermDocMatrix):
	def __init__(self,
	             X,
	             y,
	             term_idx_store,
	             category_idx_store,
	             raw_texts,
	             unigram_frequency_path=None):
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
		'''
		Returns
		-------
		pd.Series, all raw documents
		'''
		return self._raw_texts

	def search(self, ngram):
		'''
		Parameters
		----------
		ngram str or unicode, string to search for

		Returns
		-------
		pd.DataFrame, {'texts': <matching texts>, 'categories': <corresponding categories>}

		'''
		mask = self._document_index_mask(ngram)
		return pd.DataFrame({
			'text': self.get_texts()[mask],
			'category': [self._category_idx_store.getval(idx)
			             for idx in self._y[mask]]
		})

	def search_index(self, ngram):
		"""
		Parameters
		----------
		ngram str or unicode, string to search for

		Returns
		-------
		np.array, list of matching document indices
		"""
		return nonzero(self._document_index_mask(ngram))[0]

	def _document_index_mask(self, ngram):
		idx = self._term_idx_store.getidxstrict(ngram.lower())
		mask = (self._X[:, idx] > 0).todense().A1
		return mask

	def _term_doc_matrix_with_new_X(self, new_X, new_term_idx_store):
		return Corpus(X=new_X,
		              y=self._y,
		              term_idx_store=new_term_idx_store,
		              category_idx_store=self._category_idx_store,
		              raw_texts=self._raw_texts,
		              unigram_frequency_path=self._unigram_frequency_path)
