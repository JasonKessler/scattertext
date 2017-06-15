import numpy as np
import pandas as pd

from scattertext.AsianNLP import chinese_nlp
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.IndexStore import IndexStore
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory


class ParsePipelineFactory:
	def __init__(self,
	             nlp,
	             X_factory,
	             mX_factory,
	             category_idx_store,
	             term_idx_store,
	             metadata_idx_store,
	             y,
	             term_doc_mat_fact):
		if nlp == chinese_nlp:
			raise Exception("Chinese NLP not yet supported.  Preparse chinese documents, and use CorpusFromParsedDocuments or a similar class.")
		self.X_factory, self.mX_factory, self.category_idx_store, self.term_idx_store, self.metadata_idx_store, self.y, self.nlp \
			= X_factory, mX_factory, category_idx_store, term_idx_store, metadata_idx_store, y, nlp
		self._term_doc_mat_fact = term_doc_mat_fact
		self._text_col = self._term_doc_mat_fact._text_col
		self._clean_function = self._term_doc_mat_fact._clean_function
		self._verbose = self._term_doc_mat_fact._verbose
		self._register_doc_and_category \
			= self._term_doc_mat_fact._register_doc_and_category
		self._category_col \
			= self._term_doc_mat_fact._category_col

	def parse(self, row):
		cleaned_text = self._clean_function(self._get_raw_text_from_row(row))
		parsed_text = self.nlp(cleaned_text)
		if self._verbose and row.name % 100:
			print(row.name)
		self._register_document(parsed_text, row)

	def _get_raw_text_from_row(self, row):
		return row[self._text_col]

	def _register_document(self, parsed_text, row):
		self._register_doc_and_category(X_factory=self.X_factory,
		                                mX_factory=self.mX_factory,
		                                category=row[self._category_col],
		                                category_idx_store=self.category_idx_store,
		                                document_index=row.name,
		                                parsed_text=parsed_text,
		                                term_idx_store=self.term_idx_store,
		                                metadata_idx_store=self.metadata_idx_store,
		                                y=self.y)


class TermDocMatrixFromPandas(TermDocMatrixFactory):
	def __init__(self,
	             data_frame,
	             category_col,
	             text_col,
	             clean_function=lambda x: x,
	             nlp=None,
	             feats_from_spacy_doc=None,
	             verbose=False):
		'''Creates a TermDocMatrix from a pandas data frame.

		Parameters
		----------
		data_frame : pd.DataFrame
			The data frame that contains columns for the category of interest
			and the document text.
		text_col : str
			The name of the column which contains the document text.
		category_col : str
			The name of the column which contains the category of interest.
		clean_function : function, optional
		nlp : function, optional
		feats_from_spacy_doc : FeatsFromSpacyDoc or None
		verbose : boolean, optional
			If true, prints a message every time a document index % 100 is 0.

		See Also
		--------
		TermDocMatrixFactory
		'''
		TermDocMatrixFactory.__init__(self,
		                              clean_function=clean_function,
		                              nlp=nlp,
		                              feats_from_spacy_doc=feats_from_spacy_doc)
		self.data_frame = data_frame.reset_index()
		self._text_col = text_col
		self._category_col = category_col
		self._verbose = verbose

	def build(self):
		'''Constructs the term doc matrix.

		Returns
		-------
		TermDocMatrix
		'''

		X_factory, mX_factory, category_idx_store, term_idx_store, metadata_idx_store, y \
			= self._init_term_doc_matrix_variables()
		parse_pipeline = ParsePipelineFactory(self.get_nlp(),
		                                      X_factory,
		                                      mX_factory,
		                                      category_idx_store,
		                                      term_idx_store,
		                                      metadata_idx_store,
		                                      y,
		                                      self)
		df = self._clean_and_filter_nulls_and_empties_from_dataframe()
		tdm = self._apply_pipeline_and_get_build_instance(X_factory,
		                                                  mX_factory,
		                                                  category_idx_store,
		                                                  df,
		                                                  parse_pipeline,
		                                                  term_idx_store,
		                                                  metadata_idx_store,
		                                                  y)
		return tdm

	def _apply_pipeline_and_get_build_instance(self,
	                                           X_factory,
	                                           mX_factory,
	                                           category_idx_store,
	                                           df,
	                                           parse_pipeline,
	                                           term_idx_store,
	                                           metadata_idx_store,
	                                           y):
		df.apply(parse_pipeline.parse, axis=1)
		X = X_factory.get_csr_matrix()
		mX = mX_factory.get_csr_matrix()
		y = np.array(y)
		tdm = TermDocMatrix(X, mX, y, term_idx_store, category_idx_store, metadata_idx_store)
		return tdm

	def _init_term_doc_matrix_variables(self):
		return CorpusFactoryHelper.init_term_doc_matrix_variables()

	def _clean_and_filter_nulls_and_empties_from_dataframe(self):
		df = self.data_frame[[self._category_col, self._text_col]].dropna()
		df = df[(df[self._text_col] != '')].reset_index()
		return df


class CorpusFactoryHelper(object):
	@staticmethod
	def init_term_doc_matrix_variables():
		y = []
		X_factory = CSRMatrixFactory()
		mX_factory = CSRMatrixFactory()
		category_idx_store = IndexStore()
		term_idx_store = IndexStore()
		metadata_idx_store = IndexStore()

		return X_factory, mX_factory, category_idx_store, \
		       term_idx_store, metadata_idx_store, y


