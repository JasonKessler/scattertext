from unittest import TestCase

import numpy as np
import pandas as pd

from scattertext.LORIDPFactory import LORIDPFactory
from scattertext.test.test_semioticSquare import get_test_corpus


class TestLORIDPFactory(TestCase):
	def test_all_categories(self):
		corpus = get_test_corpus()
		term_scorer, my_corpus = (LORIDPFactory(corpus, starting_count=0, category='hamlet', alpha=2)
			.use_all_categories()
			.build())
		tdf = corpus.get_term_freq_df()
		self.assertEqual(len(term_scorer.get_priors()), len(tdf))
		self.assertEqual(term_scorer.alpha_w, 2)
		np.testing.assert_equal(term_scorer.get_priors().values,
		                        corpus.get_term_freq_df().sum(axis=1).values)

	def test_neutral_categories(self):
		corpus = get_test_corpus()
		term_scorer, term_doc_mat = (LORIDPFactory(corpus, 'hamlet', starting_count=0,
		                                           not_categories=['swift'], alpha=2)
			.use_neutral_categories()
			.build())
		np.testing.assert_equal(term_scorer.get_priors().values,
		                        corpus.get_term_freq_df()['jay-z/r. kelly freq'].values)

	# term_scorer.get_scores(*clean_corpus.get_term_freq_df()[['hamlet freq', 'swift freq']].values.T)

	def test_get_term_scorer_all_categories(self):
		corpus = get_test_corpus()
		fact = LORIDPFactory(corpus, 'hamlet', alpha=2)
		clean_corpus, term_scorer = fact.use_all_categories()
		self.assertEqual(corpus.get_terms(), clean_corpus.get_terms())
		np.testing.assert_equal(term_scorer.get_priors().values,
		                        corpus.get_term_freq_df().apply(sum, axis=1).values)

		corpus = get_test_corpus()
		fact = LORIDPFactory(corpus, category='hamlet', not_categories=['swift'], alpha=2)
		clean_corpus, term_scorer = fact.use_all_categories()
		self.assertEqual(corpus.get_terms(), clean_corpus.get_terms())
		np.testing.assert_equal(term_scorer.get_priors().values,
		                        corpus.get_term_freq_df().apply(sum, axis=1).values)

	def test_get_general_term_frequencies(self):
		corpus = get_test_corpus()
		fact = (LORIDPFactory(corpus,
		                      category='hamlet',
		                      not_categories=['swift'],
		                      starting_count=0.04,
		                      alpha=2)
			.use_general_term_frequencies()
			.use_all_categories()
			.drop_unused_terms()
			)
		term_scorer, clean_corpus = fact.build()
		tdf = corpus.get_term_freq_df()[['hamlet freq', 'swift freq']].sum(axis=1)
		tdf = tdf[tdf > 0]
		self.assertEqual(set(tdf.index),
		                 set(clean_corpus.get_terms()))

	def test_get_custom_term_frequencies(self):
		corpus = get_test_corpus()
		fact = (LORIDPFactory(corpus,
		                      category='hamlet',
		                      not_categories=['swift'],
		                      starting_count=0.04,
		                      alpha=2)
			.use_custom_term_frequencies(pd.Series({'halt': 3, 'i': 8}))
			.drop_zero_priors()
			)
		term_scorer, clean_corpus = fact.build()
		self.assertEqual(set(clean_corpus.get_terms()),
		                 set(['i','halt']))
