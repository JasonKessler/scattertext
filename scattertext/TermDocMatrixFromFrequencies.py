import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.indexstore import IndexStore, IndexStoreFromList


class DimensionMismatchException(Exception):
	pass


class TermDocMatrixFromFrequencies(object):
	'''
	A factory class for building a TermDocMatrix from a set of term-category frequencies.

	Note: the TermDocMatrix will assume that only K documents exist, where
	K is the number of categories.

	>>> from scattertext import TermDocMatrixFromFrequencies
	>>> from pandas import DataFrame
	>>> term_freq_df = DataFrame({
	...     'term': ['a', 'a b', 'a c', 'c', 'b', 'e b', 'e'],
	...     'A': [6, 3, 3, 3, 5, 0, 0],
	...     'B': [6, 3, 3, 3, 5, 1, 1],
	... }).set_index('term')[['A', 'B']]
	>>> term_doc_mat = TermDocMatrixFromFrequencies(term_freq_df).build()
	>>> term_doc_mat.get_categories()
	['A', 'B']
	>>> term_doc_mat.get_terms()
	['a', 'a b', 'a c', 'c', 'b', 'e b', 'e']
	'''

	def __init__(self,
	             term_freq_df,
	             unigram_frequency_path=None):
		'''
		Parameters
		----------
		term_freq_df: DataFrame
			Indexed on term, columns are counts per category
		unigram_frequency_path: str (see TermDocMatrix)
		'''
		self.term_freq_df = term_freq_df
		self.unigram_frequency_path = unigram_frequency_path

	def build(self):
		'''
		Returns
		-------
		TermDocMatrix
		'''
		constructor_kwargs = self._get_build_kwargs()
		return TermDocMatrix(
			**constructor_kwargs
		)

	def _get_build_kwargs(self):
		constructor_kwargs = {
			'X': csr_matrix(self.term_freq_df.values.T),
			'mX': csr_matrix((0, 0)),
			'y': np.array(range(len(self.term_freq_df.columns))),
			'term_idx_store': IndexStoreFromList.build(self.term_freq_df.index.values),
			'metadata_idx_store': IndexStore(),
			'category_idx_store': IndexStoreFromList.build(self.term_freq_df.columns),
			'unigram_frequency_path': self.unigram_frequency_path
		}
		return constructor_kwargs
