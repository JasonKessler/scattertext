import numpy as np
from scipy.stats import gmean

from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring import LogOddsRatioUninformativeDirichletPrior


class EmptyNeutralCategoriesError(Exception): pass


class SemioticSquare(object):
	'''
	Create a visualization of a semiotic square.  Requires Corpus to have
	at least three categories.
	>>> newsgroups_train = fetch_20newsgroups(subset='train',
	...   remove=('headers', 'footers', 'quotes'))
	>>> vectorizer = CountVectorizer()
	>>> X = vectorizer.fit_transform(newsgroups_train.data)
	>>> corpus = st.CorpusFromScikit(
	... 	X=X,
	... 	y=newsgroups_train.target,
	... 	feature_vocabulary=vectorizer.vocabulary_,
	... 	category_names=newsgroups_train.target_names,
	... 	raw_texts=newsgroups_train.data
	... 	).build()
	>>> semseq = SemioticSquare(corpus,
	... 	category_a = 'alt.atheism',
	... 	category_b = 'soc.religion.christian',
	... 	neutral_categories = ['talk.religion.misc']
	... )
	>>> # A simple HTML table
	>>> html = SemioticSquareViz(semseq).to_html()
	>>> # The table with an interactive scatterplot below it
	>>> html = st.produce_semiotic_square_explorer(semiotic_square,
	...                                            x_label='More Atheism, Less Xtnity',
	...                                            y_label='General Religious Talk')
	'''

	def __init__(self,
	             term_doc_matrix, category_a, category_b, neutral_categories,
	             # term_freq_func=lambda x: x.get_term_doc_count_df(),
	             term_ranker=AbsoluteFrequencyRanker,
	             scorer=None):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			TermDocMatrix (or descendant) which will be used in constructing square.
		category_a : str
			Category name for term A
		category_b : str
			Category name for term B (in opposition to A)
		neutral_categories : list[str]
			List of category names that A and B will be contrasted to.  Should be in same domain.
		term_ranker : TermRanker
			Class for returning a term-frequency df
		scorer : termscoring class, optional
			Term scoring class for lexicon mining. Default: `scattertext.termscoring.ScaledFScore`
		'''
		self.term_doc_matrix_ = term_doc_matrix
		assert category_a in term_doc_matrix.get_categories()
		assert category_b in term_doc_matrix.get_categories()
		for category in neutral_categories:
			assert category in term_doc_matrix.get_categories()
		if len(neutral_categories) == 0:
			raise EmptyNeutralCategoriesError()
		self.category_a_ = category_a
		self.term_ranker = term_ranker(term_doc_matrix)
		self.category_b_ = category_b
		self.neutral_categories_ = neutral_categories
		self.scorer = LogOddsRatioUninformativeDirichletPrior(alpha_w=0.001) \
			if scorer is None else scorer
		self.axes = self._build_axes(scorer)
		self._build_lexicons()

	def get_axes(self, scorer=None):
		'''
		Returns
		-------
		pd.DataFrame
		'''
		if scorer:
			return self._build_axes(scorer)
		return self.axes

	def _build_axes(self, scorer):
		if scorer is None:
			scorer = self.scorer
		tdf = self._get_term_doc_count_df()
		counts = tdf.sum(axis=1)
		tdf['x'] = scorer.get_scores(
			tdf[self.category_a_ + ' freq'],
			tdf[self.category_b_ + ' freq']
		)
		tdf['x'][np.isnan(tdf['x'])] = self.scorer.get_default_score()
		tdf['y'] = scorer.get_scores(
			tdf[[t + ' freq' for t in [self.category_a_, self.category_b_]]].sum(axis=1),
			tdf[[t + ' freq' for t in self.neutral_categories_]].sum(axis=1)
		)
		tdf['counts'] = counts
		return tdf[['x', 'y', 'counts']]

	def _get_term_doc_count_df(self):
		return (self.term_ranker.get_ranks()
		[[t + ' freq'
		  for t in [self.category_a_, self.category_b_] + self.neutral_categories_]])

	def old_get_lexicons(self, num_terms=10):
		'''
		Parameters
		----------
		num_terms : int, default 10
			Number of terms to return in each lexicon

		Returns
		-------
			dict
			 Contains the following keys, with values
			 as lists of num_terms strings
			 - category_a_words
			 - category_b_words
			 - not_category_a_and_b_words
			 - not_category_a_words
			 - not_category_b_words
			 - category_a_and_b_words
			 - category_a_vs_b_words
			 - category_b_vs_a_words
		'''
		return {
			'category_a_words': self.category_a_words_[:num_terms],
			'category_b_words': self.category_b_words_[:num_terms],
			'not_category_a_and_b_words': self.not_category_a_and_b_words_[:num_terms],
			'not_category_a_words': self.not_category_a_words_[:num_terms],
			'not_category_b_words': self.not_category_b_words_[:num_terms],
			'category_a_and_b_words': self.category_a_and_b_words_[:num_terms],
			'category_a_vs_b_words': self.category_a_vs_b_words_[:num_terms],
			'category_b_vs_a_words': self.category_b_vs_a_words_[:num_terms]
		}

	def _build_lexicons(self):
		self.lexicons = {}
		ax = self.axes
		x_max = ax['x'].max()
		y_max = ax['y'].max()
		x_min = ax['x'].min()
		y_min = ax['y'].min()
		baseline = self.scorer.get_default_score()

		def dist(candidates, x_bound, y_bound):
			return ((x_bound - candidates['x']) ** 2 + (y_bound - candidates['y']) ** 2).sort_values()

		self.lexicons['a'] = dist(ax[(ax['x'] > baseline) & (ax['y'] > baseline)], x_max, y_max)
		self.lexicons['not_a'] = dist(ax[(ax['x'] < baseline) & (ax['y'] < baseline)], x_min, y_min)

		self.lexicons['b'] = dist(ax[(ax['x'] < baseline) & (ax['y'] > baseline)], x_min, y_max)
		self.lexicons['not_b'] = dist(ax[(ax['x'] > baseline) & (ax['y'] < baseline)], x_max, y_min)

		self.lexicons['a_and_b'] = dist(ax[(ax['y'] > baseline)], baseline, y_max)
		self.lexicons['not_a_and_not_b'] = dist(ax[(ax['y'] < baseline)], baseline, y_min)

		self.lexicons['a_and_not_b'] = dist(ax[(ax['x'] > baseline)], x_max, baseline)

		self.lexicons['b_and_not_a'] = dist(ax[(ax['x'] < baseline)], x_min, baseline)

		return self.lexicons
		if False:
			tdf = self._get_term_doc_count_df()
			tdf.columns = [c.replace(' freq', '') for c in tdf.columns]
			d = {}
			d['a'] = self.scorer.get_scores(tdf[self.category_a_], tdf[self.category_b_])
			import pdb;
			pdb.set_trace()
			d['b'] = -1 * d['a']
			d['not_a'] = self.scorer.get_scores(
				tdf[[self.category_b_] + self.neutral_categories_].sum(axis=1),
				tdf[self.category_a_])
			d['not_b'] = self.scorer.get_scores(
				tdf[[self.category_a_] + self.neutral_categories_].sum(axis=1),
				tdf[self.category_b_])
			d['a_and_b'] = self.scorer.get_scores(
				tdf[[self.category_a_, self.category_b_]].sum(axis=1),
				tdf[self.neutral_categories_].sum(axis=1))
			d['not_a_and_not_b'] = -1 * d['a_and_b']
			d['a_and_not_b'] = -1 * d['not_a']
			d['b_and_not_a'] = -1 * d['not_b']
		self.lexicons = d

	def _build_lexicons_old2(self):
		tdf = self._get_term_doc_count_df()
		tdf.columns = [c.replace(' freq', '') for c in tdf.columns]
		d = {}
		d['a'] = self.scorer.get_scores(tdf[self.category_a_], tdf[self.category_b_])
		import pdb;
		pdb.set_trace()
		d['b'] = -1 * d['a']
		d['not_a'] = self.scorer.get_scores(
			tdf[[self.category_b_] + self.neutral_categories_].sum(axis=1),
			tdf[self.category_a_])
		d['not_b'] = self.scorer.get_scores(
			tdf[[self.category_a_] + self.neutral_categories_].sum(axis=1),
			tdf[self.category_b_])
		d['a_and_b'] = self.scorer.get_scores(
			tdf[[self.category_a_, self.category_b_]].sum(axis=1),
			tdf[self.neutral_categories_].sum(axis=1))
		d['not_a_and_not_b'] = -1 * d['a_and_b']
		d['a_and_not_b'] = -1 * d['not_a']
		d['b_and_not_a'] = -1 * d['not_b']
		self.lexicons = d

	def get_lexicons(self, num_terms=10):
		return {k: v.index[:num_terms]
		        for k, v in self.lexicons.items()}

	def old_build_lexicons(self):
		tdf = self._get_term_doc_count_df()
		tdf = tdf[tdf.sum(axis=1) > 0]
		self._build_lexicons_from_term_freq_df(tdf)

	def _build_lexicons_from_term_freq_df(self, tdf):
		'''

		Parameters
		----------
		tdf

		Returns
		-------

		'''

		self._find_a_vs_b_and_b_vs_a(tdf)
		tdf[self.category_a_ + ' scores'] = self.scorer.get_scores(
			tdf[self.category_a_ + ' freq'],
			tdf[[t for t in tdf.columns if t != self.category_a_ + ' freq']].sum(axis=1)
		)
		tdf[self.category_b_ + ' scores'] = self.scorer.get_scores(
			tdf[self.category_b_ + ' freq'],
			tdf[[t for t in tdf.columns if t != self.category_b_ + ' freq']].sum(axis=1))
		tdf[self.category_a_ + ' + ' + self.category_b_ + ' scores'] = tdf[
			[t + ' scores' for t in [self.category_a_, self.category_b_]]].apply(
			lambda x: gmean(x) if min(x) > 0 else 0, axis=1)
		tdf["not " + self.category_a_ + ' scores'] = self.scorer.get_scores(
			tdf[[t for t in tdf.columns if t != self.category_a_ + ' freq']].sum(axis=1),
			tdf[self.category_a_ + ' freq'])
		tdf["not " + self.category_b_ + ' scores'] = self.scorer.get_scores(
			tdf[[t for t in tdf.columns if t != self.category_b_ + ' freq']].sum(axis=1),
			tdf[self.category_b_ + ' freq'])
		tdf["not " + self.category_a_ + ' + ' + self.category_b_ + ' scores'] = tdf[
			['not ' + t + ' scores' for t in [self.category_a_, self.category_b_]]].apply(
			lambda x: gmean(x) if min(x) > 0 else 0, axis=1)
		self.category_a_words_ = list(tdf.sort_values(by=self.category_a_ + ' scores',
		                                              ascending=False).index)
		self.category_b_words_ = list(tdf.sort_values(by=self.category_b_ + ' scores',
		                                              ascending=False).index)
		self.category_a_and_b_words_ = list(
			tdf.sort_values(by=self.category_a_ + ' + ' + self.category_b_ + ' scores',
			                ascending=False).index)
		self.not_category_a_words_ = list(
			tdf.sort_values(by='not ' + self.category_a_ + ' scores',
			                ascending=False).index)
		self.not_category_b_words_ = list(
			tdf.sort_values(by='not ' + self.category_b_ + ' scores',
			                ascending=False).index)
		self.not_category_a_and_b_words_ = list(
			tdf.sort_values(by='not ' + self.category_a_ + ' + ' + self.category_b_ + ' scores',
			                ascending=False).index)

	def _find_a_vs_b_and_b_vs_a(self, tdf):
		term_tdf = tdf[[self.category_a_ + ' freq', self.category_b_ + ' freq']]
		term_tdf = term_tdf[term_tdf.sum(axis=1) > 0]
		term_tdf[self.category_a_ + ' scores'] = self.scorer.get_scores(
			term_tdf[self.category_a_ + ' freq'],
			term_tdf[self.category_b_ + ' freq'])
		term_tdf[self.category_b_ + ' scores'] = self.scorer.get_scores(
			term_tdf[self.category_b_ + ' freq'],
			term_tdf[self.category_a_ + ' freq'])
		self.category_a_vs_b_words_ = list(term_tdf.sort_values(by=self.category_a_ + ' scores',
		                                                        ascending=False).index)
		self.category_b_vs_a_words_ = list(term_tdf.sort_values(by=self.category_b_ + ' scores',
		                                                        ascending=False).index)
