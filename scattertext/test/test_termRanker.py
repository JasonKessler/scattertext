from unittest import TestCase

import numpy as np

from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termranking import DocLengthDividedFrequencyRanker
from scattertext.termranking import DocLengthNormalizedFrequencyRanker
from scattertext.termranking.OncePerDocFrequencyRanker import OncePerDocFrequencyRanker
from scattertext.test.test_TermDocMat import make_a_test_term_doc_matrix


class TestTermRanker(TestCase):
	def test_absolute_frequency_ranker(self):
		tdm = make_a_test_term_doc_matrix()
		ranker = AbsoluteFrequencyRanker(tdm)
		rank_df = ranker.get_ranks()
		self.assertEqual(len(rank_df), 58)
		self.assertEqual(rank_df.ix['hello'].tolist(), [1, 0])
		self.assertEqual(rank_df.ix['blah'].tolist(), [0, 3])
		self.assertEqual(rank_df.ix['name'].tolist(), [1, 1])

	def test_doc_length_normalized_frequency_ranker(self):
		tdm = make_a_test_term_doc_matrix()
		len_ranker = DocLengthNormalizedFrequencyRanker(tdm)
		abs_ranker = AbsoluteFrequencyRanker(tdm)
		abs_rank_df = abs_ranker.get_ranks()
		len_ranker_df = len_ranker.get_ranks()
		self.assertEqual(len(abs_rank_df), len(len_ranker_df))
		doc_lengths = [12, 35, 29]
		avg_length = sum(doc_lengths) * 1. / len(doc_lengths)
		np.testing.assert_almost_equal(np.array(len_ranker_df.ix['blah']),
		                               [0, avg_length * 3. / 12])
		np.testing.assert_almost_equal(np.array(len_ranker_df.ix['name']),
		                               [avg_length * 1. / 35, avg_length * 1. / 29])

	def test_doc_length_divided_frequency_ranker(self):
		tdm = make_a_test_term_doc_matrix()
		len_ranker = DocLengthDividedFrequencyRanker(tdm)
		abs_ranker = AbsoluteFrequencyRanker(tdm)
		abs_rank_df = abs_ranker.get_ranks()
		len_ranker_df = len_ranker.get_ranks()
		self.assertEqual(len(abs_rank_df), len(len_ranker_df))
		doc_lengths = [12, 35, 29]
		np.testing.assert_almost_equal(np.array(len_ranker_df.ix['blah']),
		                               [0, 3. / 12])
		np.testing.assert_almost_equal(np.array(len_ranker_df.ix['name']),
		                               [1. / 35, 1. / 29])


	def test_once_per_doc_frequency_ranker(self):
		tdm = make_a_test_term_doc_matrix()
		abs_ranker = DocLengthDividedFrequencyRanker(tdm)

		one_ranker = OncePerDocFrequencyRanker(tdm)
		abs_rank_df = abs_ranker.get_ranks()
		len_ranker_df = one_ranker.get_ranks()
		self.assertEqual(len(abs_rank_df), len(len_ranker_df))
		np.testing.assert_almost_equal(np.array(len_ranker_df.ix['blah']),
		                               [0, 1])
		np.testing.assert_almost_equal(np.array(len_ranker_df.ix['name']),
		                               [1, 1])
