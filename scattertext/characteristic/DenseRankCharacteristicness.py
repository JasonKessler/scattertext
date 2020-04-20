import pandas as pd
from scipy.stats import rankdata

from scattertext.Scalers import scale
from scattertext.frequencyreaders.DefaultBackgroundFrequencies import DefaultBackgroundFrequencies
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference


class CharacteristicScorer(object):
	def __init__(self,
	             term_ranker=AbsoluteFrequencyRanker,
	             background_frequencies=DefaultBackgroundFrequencies,
	             rerank_ranks=False):
		'''
		Parameters
		----------
		term_ranker : TermRanker, default is OncePerDocFrequencyRanker
		background_frequencies : BackgroundFrequencies
		rerank_ranks : bool, False by default
			orders scores from 0 to 1 by their dense rank
		'''
		self.term_ranker = term_ranker
		self.background_frequencies = background_frequencies
		self.rerank_ranks = rerank_ranks

	def get_scores(self, corpus):
		raise Exception()

	def _rerank_scores(self, scores):
		ranks = rankdata(scores, 'dense')
		ranks = ranks / ranks.max()
		return ranks, 0.5


class DenseRankCharacteristicness(CharacteristicScorer):
	def get_scores(self, corpus):
		'''
		Parameters
		----------
		corpus

		Returns
		-------
		float, pd.Series
		float: point on x-axis at even characteristicness
		pd.Series: term -> value between 0 and 1, sorted by score in a descending manner
		Background scores from corpus
		'''
		term_ranks = self.term_ranker(corpus).get_ranks()

		freq_df = pd.DataFrame({
			'corpus': term_ranks.sum(axis=1),
			'standard': self.background_frequencies.get_background_frequency_df()[
				'background'
			]
		})

		freq_df = freq_df.loc[freq_df['corpus'].dropna().index].fillna(0)

		corpus_rank = rankdata(freq_df.corpus, 'dense')
		standard_rank = rankdata(freq_df.standard, 'dense')
		scores = corpus_rank/corpus_rank.max() - standard_rank/standard_rank.max()

		if self.rerank_ranks:
			rank_scores, zero_marker = self._rerank_scores(scores)
			freq_df['score'] = pd.Series(rank_scores, index=freq_df.index)
		else:
			if scores.min() < 0 and scores.max() > 0:
				zero_marker = -scores.min() / (scores.max() - scores.min())
			elif scores.min() > 0:
				zero_marker = 0
			else:
				zero_marker = 1
			freq_df['score'] = scale(scores)
		return zero_marker, freq_df.sort_values(by='score', ascending=False)['score']
