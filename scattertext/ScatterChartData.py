import numpy as np

from scattertext.termranking import AbsoluteFrequencyRanker


class ScatterChartData(object):
	def __init__(self,
	             minimum_term_frequency=3,
	             minimum_not_category_term_frequency=0,
	             jitter=None,
	             seed=0,
	             pmi_threshold_coefficient=3,
	             max_terms=None,
	             filter_unigrams=False,
	             term_ranker=AbsoluteFrequencyRanker,
	             use_non_text_features=False,
	             term_significance=None,
	             terms_to_include=None):
		'''

		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			The term doc matrix to use for the scatter chart.
		minimum_term_frequency : int, optional
			Minimum times an ngram has to be seen to be included. Default is 3.
		minimum_not_category_term_frequency : int, optional
		  If an n-gram does not occur in the category, minimum times it
		   must been seen to be included. Default is 0.
		jitter : float, optional
			Maximum amount of noise to be added to points, 0.2 is a lot. Default is None to disable jitter.
		seed : float, optional
			Random seed. Default 0
		pmi_threshold_coefficient : int
			Filter out bigrams with a PMI of < 2 * pmi_threshold_coefficient. Default is 3
		max_terms : int, optional
			Maximum number of terms to include in visualization
		filter_unigrams : bool, optional
			If True, remove unigrams that are part of bigrams. Default is False.
		term_ranker : TermRanker, optional
			TermRanker class for determining term frequency ranks.
		use_non_text_features : bool, default = False
			Use non-BoW features (e.g., Empath) instead of text features
		term_significance : TermSignificance instance or None
			Way of getting significance scores.  If None, p values will not be added.
		terms_to_include : set or None
			Only annotate these terms in chart
		'''
		self.jitter = jitter
		self.minimum_term_frequency = minimum_term_frequency
		self.minimum_not_category_term_frequency = minimum_not_category_term_frequency
		self.seed = seed
		self.pmi_threshold_coefficient = pmi_threshold_coefficient
		self.filter_unigrams = filter_unigrams
		self.term_ranker = term_ranker
		self.max_terms = max_terms
		self.use_non_text_features = use_non_text_features
		self.term_significance = term_significance
		self.terms_to_include = terms_to_include
		np.random.seed(seed)