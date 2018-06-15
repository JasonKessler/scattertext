import numpy as np

from scattertext import CorpusDF
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.indexstore.IndexStore import IndexStore


class CorpusFromFeatureDict(object):
	def __init__(self,
	             df,
	             category_col,
	             text_col,
	             feature_col,
	             metadata_col=None,
	             parsed_col=None):

		'''
		Parameters
		----------
		df : pd.DataFrame
		 contains category_col, and parse_col, were parsed col is entirely spacy docs
		category_col : str
				name of category column in convention_df
		text_col : str
				The name of the column which contains each document's raw text.
		feature_col : str
				name of column in convention_df with a feature dictionary
		metadata_col : str, optional
				name of column in convention_df with a meatadata dictionary
		parsed_col : str, optional
				name of column in convention_df with parsed strings
		'''
		self._df = df.reset_index()
		self._category_col = category_col
		self._text_col = text_col
		self._feature_col = feature_col
		self._parsed_col = parsed_col
		self._metadata_col = metadata_col
		self._category_idx_store = IndexStore()
		self._X_factory = CSRMatrixFactory()
		self._mX_factory = CSRMatrixFactory()
		self._term_idx_store = IndexStore()
		self._metadata_idx_store = IndexStore()

	def build(self):
		'''Constructs the term doc matrix.

		Returns
		-------
		scattertext.ParsedCorpus.ParsedCorpus
		'''
		self._y = self._get_y_and_populate_category_idx_store()
		self._df.apply(self._add_to_x_factory, axis=1)
		self._X = self._X_factory.set_last_row_idx(len(self._y) - 1).get_csr_matrix()
		self._mX = self._mX_factory.set_last_row_idx(len(self._y) - 1).get_csr_matrix()
		if self._parsed_col is not None and self._parsed_col in self._df:
			return ParsedCorpus(self._df,
			                    self._X,
			                    self._mX,
			                    self._y,
			                    self._term_idx_store,
			                    self._category_idx_store,
			                    self._metadata_idx_store,
			                    self._parsed_col,
			                    self._category_col)
		else:
			return CorpusDF(self._df,
			                self._X,
			                self._mX,
			                self._y,
			                self._text_col,
			                self._term_idx_store,
			                self._category_idx_store,
			                self._metadata_idx_store)

	def _get_y_and_populate_category_idx_store(self):
		return np.array(self._df[self._category_col].apply(self._category_idx_store.getidx))

	def _add_to_x_factory(self, row):
		for feat, count in row[self._feature_col].items():
			feat_idx = self._term_idx_store.getidx(feat)
			self._X_factory[row.name, feat_idx] = count
		if self._metadata_col in self._df:
			for meta, count in row[self._metadata_col].items():
				meta_idx = self._metadata_idx_store.getidx(meta)
				self._mX_factory[row.name, meta_idx] = count

	def _make_new_term_doc_matrix(self,
	                              new_X,
	                              new_mX,
	                              new_y,
	                              new_term_idx_store,
	                              new_category_idx_store,
	                              new_metadata_idx_store,
	                              new_y_mask):
		if self._parsed_col is not None and self._parsed_col in self._df:
			return ParsedCorpus(self._df[new_y_mask],
			                    new_X,
			                    new_mX,
			                    new_y,
			                    new_term_idx_store,
			                    new_category_idx_store,
			                    new_metadata_idx_store,
			                    self._parsed_col,
			                    self._category_col)
		else:
			return CorpusDF(self._df[new_y_mask],
			                new_X,
			                new_mX,
			                new_y,
			                self._text_col,
			                new_term_idx_store,
			                new_category_idx_store,
			                new_metadata_idx_store,
			                self._df[self._text_col][new_y_mask])
