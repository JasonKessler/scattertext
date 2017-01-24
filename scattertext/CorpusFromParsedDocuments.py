from scattertext.IndexStore import IndexStore
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc
import numpy as np

class CorpusFromParsedDocuments(object):
	def __init__(self,
	             df,
	             category_col,
	             parsed_col,
	             feats_from_spacy_doc=FeatsFromSpacyDoc()):

		'''
		Parameters
		----------
		df : pd.DataFrame
		 contains category_col, and parse_col, were parsed col is entirely spacy docs
		category_col : str
			name of category column in df
		parsed_col : str
			name of spacy parsed column in df
		feats_from_spacy_doc : FeatsFromSpacyDoc
		'''
		self._df = df.reset_index()
		self._category_col = category_col
		self._parsed_col = parsed_col

		self._category_idx_store = IndexStore()
		self._X_factory = CSRMatrixFactory()
		self._mX_factory = CSRMatrixFactory()
		self._term_idx_store = IndexStore()
		self._metadata_idx_store = IndexStore()
		self._feats_from_spacy_doc = feats_from_spacy_doc

	def build(self):
		'''Constructs the term doc matrix.

		Returns
		-------
		scattertext.ParsedCorpus.ParsedCorpus
		'''
		self._y = self._get_y_and_populate_category_idx_store()
		self._df.apply(self._add_to_x_factory, axis=1)
		self._X = self._X_factory.get_csr_matrix()
		self._mX = self._mX_factory.get_csr_matrix()
		return ParsedCorpus(self._df,
		                    self._X,
		                    self._mX,
		                    self._y,
		                    self._term_idx_store,
		                    self._category_idx_store,
		                    self._metadata_idx_store,
		                    self._parsed_col,
		                    self._category_col)

	def _get_y_and_populate_category_idx_store(self):
		return np.array(self._df[self._category_col].apply(self._category_idx_store.getidx))

	def _add_to_x_factory(self, row):
		parsed_text = row[self._parsed_col]
		for term, count in self._feats_from_spacy_doc.get_feats(parsed_text).items():
			term_idx = self._term_idx_store.getidx(term)
			self._X_factory[row.name, term_idx] = count
		for meta, val in self._feats_from_spacy_doc.get_doc_metadata(parsed_text).items():
			meta_idx = self._metadata_idx_store.getidx(meta)
			self._mX_factory[row.name, meta_idx] = val