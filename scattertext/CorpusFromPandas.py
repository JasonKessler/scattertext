import numpy as np

from scattertext import CorpusDF
from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas, build_sparse_matrices


class CorpusFromPandas(TermDocMatrixFromPandas):
	'''Creates a Corpus from a pandas data frame.  A Corpus is a Term Document Matrix
	preserves the original texts.

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
		A function that strips invalid characters out of the document text string, returning
		a new string.
	nlp : function, optional
	verbose : boolean, optional
		If true, prints a message every time a document index % 100 is 0.

	See Also
	--------
	TermDocMatrixFromPandas
	'''

	def _apply_pipeline_and_get_build_instance(self,
	                                           X_factory,
	                                           mX_factory,
	                                           category_idx_store,
	                                           df,
	                                           parse_pipeline,
	                                           term_idx_store,
	                                           metadata_idx_store,
	                                           y):
		'''
		Parameters
		----------
		X_factory
		mX_factory
		category_idx_store
		df
		parse_pipeline
		term_idx_store
		metadata_idx_store
		y

		Returns
		-------
		CorpusDF
		'''
		df.apply(parse_pipeline.parse, axis=1)
		y = np.array(y)
		X, mX = build_sparse_matrices(y, X_factory, mX_factory)
		return CorpusDF(df,
		                X,
		                mX,
		                y,
		                self._text_col,
		                term_idx_store,
		                category_idx_store,
		                metadata_idx_store)
