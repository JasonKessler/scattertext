from unittest import TestCase

import numpy as np
import pandas as pd

from scattertext import LogOddsRatioInformativeDirichletPrior
from scattertext.PriorFactory import PriorFactory
from scattertext.test.test_semioticSquare import get_test_corpus


class TestPriorFactory(TestCase):
	def test_all_categories(self):
		corpus = get_test_corpus()
		priors, my_corpus = (PriorFactory(corpus, starting_count=0, category='hamlet')
			.use_all_categories()
			.build())
		tdf = corpus.get_term_freq_df()
		self.assertEqual(len(priors), len(tdf))
		np.testing.assert_equal(priors.values,
		                        corpus.get_term_freq_df().sum(axis=1).values)

	def test_neutral_categories(self):
		corpus = get_test_corpus()
		priors= (PriorFactory(corpus, 'hamlet', starting_count=0.001,
		                                     not_categories=['swift'])
			.use_neutral_categories()
			.get_priors())
		self.assertEqual(priors.min(), 0.001)
		self.assertEqual(priors.shape[0], corpus._X.shape[1])

		corpus = get_test_corpus()
		priors = (PriorFactory(corpus, 'hamlet', starting_count=0.001,
		                       not_categories=['swift'])
			.use_neutral_categories()
			.drop_zero_priors()
			.get_priors())

		jzcnts = corpus.get_term_freq_df()['jay-z/r. kelly freq'].where(lambda x: x > 0).dropna()
		np.testing.assert_equal(priors.values,
		                        jzcnts.values + 0.001)

	def test_get_general_term_frequencies(self):
		corpus = get_test_corpus()
		fact = (PriorFactory(corpus,
		                     category='hamlet',
		                     not_categories=['swift'],
		                     starting_count=0)
			.use_general_term_frequencies()
			.use_all_categories()
			)
		priors, clean_corpus = fact.build()

		expected_prior = pd.merge(corpus.get_term_doc_count_df(),
		                          corpus.get_term_and_background_counts()[['background']],
		                          left_index=True,
		                          right_index=True,
		                          how='left').fillna(0.).sum(axis=1)

		np.testing.assert_allclose(priors.values, expected_prior.values)


	def test_align_to_target(self):
		full_corpus = get_test_corpus()
		corpus = full_corpus.remove_categories(['swift'])
		priors = PriorFactory(full_corpus).use_all_categories().get_priors()
		with self.assertRaises(ValueError):
			(LogOddsRatioInformativeDirichletPrior(priors)
			 .get_scores(*corpus.get_term_freq_df().values.T))
		priors = (PriorFactory(full_corpus)
		          .use_all_categories()
		          .align_to_target(corpus)
		          .get_priors())
		(LogOddsRatioInformativeDirichletPrior(priors)
		 .get_scores(*corpus.get_term_freq_df().values.T))

	def test_use_categories(self):
		full_corpus = get_test_corpus()
		priors = PriorFactory(full_corpus).use_categories(['swift']).get_priors()
		corpus = full_corpus.remove_categories(['swift'])
		with self.assertRaises(ValueError):
			(LogOddsRatioInformativeDirichletPrior(priors)
			 .get_scores(*corpus.get_term_freq_df().values.T))
		priors = (PriorFactory(full_corpus)
		          .use_all_categories()
		          .align_to_target(corpus)
		          .get_priors())
		(LogOddsRatioInformativeDirichletPrior(priors)
		 .get_scores(*corpus.get_term_freq_df().values.T))

	def test_get_custom_term_frequencies(self):
		corpus = get_test_corpus()
		fact = (PriorFactory(corpus, starting_count=0.04)
			.use_custom_term_frequencies(pd.Series({'halt': 3, 'i': 8}))
			.drop_zero_priors()
			)
		priors, clean_corpus = fact.build()
		self.assertEqual(set(clean_corpus.get_terms()), {'i', 'halt'})
		np.testing.assert_equal(priors.sort_values().values, [3.04, 8.04])
