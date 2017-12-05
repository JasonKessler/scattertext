import numpy as np

from scattertext import Corpus
from scattertext.TermDocMatrixFromScikit import TermDocMatrixFromScikit


class CorpusFromScikit(TermDocMatrixFromScikit):
	'''
	Tie-in to incorporate sckit-learn's various vectorizers into Scattertext
	>>> from sklearn.datasets import fetch_20newsgroups
	>>> from sklearn.feature_extraction.text import CountVectorizer
	>>> from scattertext.CorpusFromScikit import CorpusFromScikit
	>>> newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
	>>> count_vectorizer = CountVectorizer()
	>>> X_counts = count_vectorizer.fit_transform(newsgroups_train.data)
	>>> corpus = CorpusFromScikit(
	...     X=X_counts,
	...     y=newsgroups_train.target,
	...     feature_vocabulary=count_vectorizer.vocabulary_,
	...     category_names=newsgroups_train.target_names,
	...     raw_texts=newsgroups_train.data
	... ).build()
	'''
	def __init__(self,
	             X,
	             y,
	             feature_vocabulary,
	             category_names,
	             raw_texts,
	             unigram_frequency_path=None):
		'''
		Parameters
		----------
		X: sparse matrix integer, giving term-document-matrix counts
		y: list, integer categories
		feature_vocabulary: dict (feat_name -> idx)
		category_names: list of category names (len of y)
		raw_texts: array-like of raw texts
		unigram_frequency_path: str (see TermDocMatrix)

		'''
		TermDocMatrixFromScikit.__init__(self, X, y, feature_vocabulary,
		                                 category_names, unigram_frequency_path)
		self.raw_texts = raw_texts

	def build(self):
		'''
		Returns
		-------
		Corpus
		'''
		constructor_kwargs = self._get_build_kwargs()
		if type(self.raw_texts) == list:
			constructor_kwargs['raw_texts'] = np.array(self.raw_texts)
		else:
			constructor_kwargs['raw_texts'] = self.raw_texts
		return Corpus(**constructor_kwargs)
