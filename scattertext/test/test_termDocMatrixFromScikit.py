from unittest import TestCase

from scattertext import TermDocMatrixFromScikit


class TestTermDocMatrixFromScikit(TestCase):
	def test_build(self):
		from sklearn.datasets import fetch_20newsgroups
		from sklearn.feature_extraction.text import CountVectorizer
		newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
		count_vectorizer = CountVectorizer()
		X_counts = count_vectorizer.fit_transform(newsgroups_train.data)
		term_doc_mat = TermDocMatrixFromScikit(
			X=X_counts,
			y=newsgroups_train.target,
			feature_vocabulary=count_vectorizer.vocabulary_,
			category_names=newsgroups_train.target_names).build()
		self.assertEqual(term_doc_mat.get_categories()[:2], ['alt.atheism', 'comp.graphics'])
		self.assertEqual(term_doc_mat
		                 .get_term_freq_df()
		                 .assign(score=term_doc_mat.get_scaled_f_scores('alt.atheism'))
		                 .sort_values(by='score', ascending=False).index.tolist()[:5],
		                 ['atheism', 'atheists', 'islam', 'atheist', 'matthew'])
