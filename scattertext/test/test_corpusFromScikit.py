from unittest import TestCase

from scattertext.CorpusFromScikit import CorpusFromScikit


class TestCorpusFromScikit(TestCase):
	def test_main(self):
		# omitting for travis ci
		pass
	def _te_ss_t_build(self):
		from sklearn.datasets import fetch_20newsgroups
		from sklearn.feature_extraction.text import CountVectorizer

		newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
		count_vectorizer = CountVectorizer()
		X_counts = count_vectorizer.fit_transform(newsgroups_train.data)
		corpus = CorpusFromScikit(
			X=X_counts,
			y=newsgroups_train.target,
			feature_vocabulary=count_vectorizer.vocabulary_,
			category_names=newsgroups_train.target_names,
			raw_texts=newsgroups_train.data
		).build()
		self.assertEqual(corpus.get_categories()[:2], ['alt.atheism', 'comp.graphics'])
		self.assertEqual(corpus
		                 .get_term_freq_df()
		                 .assign(score=corpus.get_scaled_f_scores('alt.atheism'))
		                 .sort_values(by='score', ascending=False).index.tolist()[:5],
		                 ['atheism', 'atheists', 'islam', 'atheist', 'belief'])
		self.assertGreater(len(corpus.get_texts()[0]), 5)
