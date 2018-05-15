import pandas as pd

from scattertext import DefaultBackgroundFrequencies
from scattertext.Scalers import scale
from scattertext.termranking import OncePerDocFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference


class CharacteristicScorer(object):
	def __init__(self, term_ranker=OncePerDocFrequencyRanker, background_frequencies=DefaultBackgroundFrequencies):
		'''
		Parameters
		----------
		term_ranker : TermRanker, default is OncePerDocFrequencyRanker
		background_frequencies :
		'''
		self.term_ranker = term_ranker
		self.background_frequencies = background_frequencies

	def get_scores(self, corpus):
		raise Exception()


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

		bg = pd.DataFrame({'corpus': term_ranks.sum(axis=1),
		                   'bg': self.background_frequencies.get_background_frequency_df()['background']}).dropna()
		scores = RankDifference().get_scores(bg['corpus'], bg['bg']).sort_values()
		if scores.min() < 0 and scores.max() > 0:
			zero_marker = -scores.min() / (scores.max() - scores.min())
		elif scores.min() > 0:
			zero_marker = 0
		else:
			zero_marker = 1
		bg['score'] = scale(scores)
		return zero_marker, bg.sort_values(by='score', ascending=False)['score']
