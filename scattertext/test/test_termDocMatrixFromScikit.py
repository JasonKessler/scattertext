from unittest import TestCase

import numpy as np

from scattertext import TermDocMatrixFromScikit
from scattertext.indexstore import IndexStore
from scattertext.test.test_semioticSquare import get_docs_categories_semiotic


class TestTermDocMatrixFromScikit(TestCase):
	def test_build(self):
		from sklearn.feature_extraction.text import CountVectorizer
		categories, docs = get_docs_categories_semiotic()
		idx_store = IndexStore()
		y = np.array([idx_store.getidx(c) for c in categories])
		count_vectorizer = CountVectorizer()
		X_counts = count_vectorizer.fit_transform(docs)
		term_doc_mat = TermDocMatrixFromScikit(
			X=X_counts,
			y=y,
			feature_vocabulary=count_vectorizer.vocabulary_,
			category_names=idx_store.values()).build()
		self.assertEqual(term_doc_mat.get_categories()[:2], ['hamlet', 'jay-z/r. kelly'])
		self.assertEqual(term_doc_mat
		                 .get_term_freq_df()
		                 .assign(score=term_doc_mat.get_scaled_f_scores('hamlet'))
		                 .sort_values(by='score', ascending=False).index.tolist()[:5],
		                 ['that', 'march', 'did', 'majesty', 'sometimes'])
