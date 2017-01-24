import numpy as np

from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas
from scattertext.Corpus import Corpus


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
		nlp : function, optional
		use_lemmas : boolean, optional
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
		df.apply(parse_pipeline.parse, axis=1)
		X = X_factory.get_csr_matrix()
		mX = mX_factory.get_csr_matrix()
		y = np.array(y)
		raw_texts = df[self._text_col]
		return Corpus(X, mX, y, term_idx_store, category_idx_store, metadata_idx_store, raw_texts)