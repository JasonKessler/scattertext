from scattertext.TermDocMatrix import TermDocMatrix

from scattertext.indexstore import IndexStore, IndexStoreFromList, IndexStoreFromDict
from scipy.sparse import csr_matrix


class DimensionMismatchException(Exception):
	pass


class TermDocMatrixFromScikit(object):
	'''
	A factory class for building a TermDocMatrix from a scikit-learn-processed
	dataset.

	>>> from scattertext import TermDocMatrixFromScikit
	>>> from sklearn.datasets import fetch_20newsgroups
	>>> from sklearn.feature_extraction.text import CountVectorizer
	>>> newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
	>>> count_vectorizer = CountVectorizer()
	>>> X_counts = count_vectorizer.fit_transform(newsgroups_train.data)
	>>> term_doc_mat = TermDocMatrixFromScikit(
	...   X = X_counts,
	...   y = newsgroups_train.target,
	...   feature_vocabulary=count_vectorizer.vocabulary_,
	...   category_names=newsgroups_train.target_names
	... ).build()
	>>> term_doc_mat.get_categories()[:2]
	['alt.atheism', 'comp.graphics']
	>>> term_doc_mat.get_term_freq_df().assign(score=term_doc_mat.get_scaled_f_scores('alt.atheism')).sort_values(by='score', ascending=False).index.tolist()[:5]
	['atheism', 'atheists', 'islam', 'atheist', 'matthew']
	'''
	def __init__(self,
	             X,
	             y,
	             feature_vocabulary,
	             category_names,
	             unigram_frequency_path=None):
		'''
		Parameters
		----------
		X: sparse matrix integer, giving term-document-matrix counts
		y: list, integer categories
		feature_vocabulary: dict (feat_name -> idx)
		category_names: list of category names (len of y)
		unigram_frequency_path: str (see TermDocMatrix)
		'''

		if X.shape != (len(y), len(feature_vocabulary)):
			raise DimensionMismatchException('The shape of X is expected to be ' +
			                                 str((len(y), len(feature_vocabulary))) +
			                                 'but was actually: ' + str(X.shape))
		self.X = X
		self.y = y
		self.feature_vocabulary = feature_vocabulary
		self.category_names = category_names
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
		constructor_kwargs = {'X': self.X,
		                      'mX': csr_matrix((0, 0)),
		                      'y': self.y,
		                      'term_idx_store': IndexStoreFromDict.build(self.feature_vocabulary),
		                      'metadata_idx_store': IndexStore(),
		                      'category_idx_store': IndexStoreFromList.build(self.category_names),
		                      'unigram_frequency_path': self.unigram_frequency_path}
		return constructor_kwargs
