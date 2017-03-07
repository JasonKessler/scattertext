import numpy as np
import pandas as pd
from scipy.stats import rankdata

from scattertext.PValGetter import get_p_vals
from scattertext.Scalers import percentile_min, percentile_alphabetical
from scattertext.TermDocMatrixFilter import filter_bigrams_by_pmis, \
	filter_out_unigrams_that_only_occur_in_one_bigram
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring import ScaledFScore
from scattertext.termscoring.RudderScore import RudderScore


class NoWordMeetsTermFrequencyRequirementsError(Exception):
	pass


class ScatterChart:
	def __init__(self,
	             term_doc_matrix,
	             minimum_term_frequency=3,
	             jitter=0,
	             seed=0,
	             pmi_threshold_coefficient=3,
	             max_terms=None,
	             filter_unigrams=False,
	             term_ranker=AbsoluteFrequencyRanker,
	             use_non_text_features=False,
	             term_significance=None):

		'''

		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			The term doc matrix to use for the scatter chart.
		minimum_term_frequency : int, optional
			Minimum times an ngram has to be seen to be included. Default is 3.
		jitter : float, optional
			Maximum amount of noise to be added to points, 0.2 is a lot. Default is 0.
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
		term_significance : TermSignifiance instance or None
			Way of getting signfiance scores.  If None, p values will not be added.
		'''
		self.term_doc_matrix = term_doc_matrix
		self.jitter = jitter
		self.minimum_term_frequency = minimum_term_frequency
		self.seed = seed
		self.pmi_threshold_coefficient = pmi_threshold_coefficient
		self.filter_unigrams = filter_unigrams
		self.term_ranker = term_ranker
		self.max_terms = max_terms
		self.use_non_text_features = use_non_text_features
		self.term_significance = term_significance
		np.random.seed(seed)

	def to_dict(self,
	            category,
	            category_name=None,
	            not_category_name=None,
	            scores=None,
	            transform=percentile_alphabetical):
		'''

		Parameters
		----------
		category : str
			Category to annotate.  Exact value of category.
		category_name : str, optional
			Name of category which will appear on web site. Default None is same as category.
		not_category_name : str, optional
			Name of ~category which will appear on web site. Default None is same as "not " + category.
		scores : np.array, optional
			Scores to use for coloring.  Defaults to None, or np.array(self.term_doc_matrix.get_scaled_f_scores(category))
		transform : function, optional
			Function for ranking terms.  Defaults to scattertext.Scalers.percentile_lexicographic.

		Returns
		-------
		Dictionary that encodes the scatter chart
		information. The dictionary can be dumped as a json document, and
		used in scattertext.html
		 {info: {category_name: ..., not_category_name},
		  data: [{term:,
		          x:frequency [0-1],
		          y:frequency [0-1],
              s: score,
              os: original score,
              p: p-val,
              cat25k: freq per 25k in category,
              cat: count in category,
              ncat: count in non-category,
              catdocs: [docnum, ...],
              ncatdocs: [docnum, ...]
              ncat25k: freq per 25k in non-category}, ...]}}

		'''
		all_categories, other_categories = self._get_category_names(category)
		df = self._term_rank_score_and_frequency_df(all_categories, category, scores)
		df['x'], df['y'] = self._get_coordinates_from_transform_and_jitter_frequencies \
			(category, df, other_categories, transform)
		df['not cat freq'] = df[[x for x in other_categories]].sum(axis=1)
		json_df = df[['x', 'y', 'term']]
		if self.term_significance:
			json_df['p'] = df['p']
		self._add_term_freq_to_json_df(json_df, df, category)
		json_df['s'] = percentile_min(df['color_scores'])
		json_df['os'] = df['color_scores']
		if not self.use_non_text_features:
			json_df['bg'] = self._get_corpus_characteristic_scores(json_df)

		category_terms = list(json_df.sort_values('s')['term'][:10])
		not_category_terms = list(json_df.sort_values('s')['term'][:10])
		if category_name is None:
			category_name = category
		if not_category_name is None:
			not_category_name = 'Not ' + category_name

		def better_title(x):
			return ' '.join([t[0].upper() + t[1:].lower() for t in x.split()])

		j = {'info': {'category_name': better_title(category_name),
		              'not_category_name': better_title(not_category_name),
		              'category_terms': category_terms,
		              'not_category_terms': not_category_terms,
		              'category_internal_name': category}}
		j['data'] = json_df.sort_values(by=['x', 'y', 'term']).to_dict(orient='records')
		return j

	def _get_corpus_characteristic_scores(self, json_df):
		bg_terms = self.term_doc_matrix.get_scaled_f_scores_vs_background()
		bg_terms = bg_terms['Scaled f-score']
		bg_terms.name = 'bg'
		bg_terms = bg_terms.reset_index()
		bg_terms.columns = ['term' if x == 'index' else x for x in bg_terms.columns]
		json_df = pd.merge(json_df, bg_terms, on='term', how='left')
		return json_df['bg'].fillna(0)

	def _add_term_freq_to_json_df(self, json_df, term_freq_df, category):
		json_df['cat25k'] = (((term_freq_df[category + ' freq'] * 1.
		                       / term_freq_df[category + ' freq'].sum()) * 25000)
		                     .apply(np.round).astype(np.int))
		json_df['ncat25k'] = (((term_freq_df['not cat freq'] * 1.
		                        / term_freq_df['not cat freq'].sum()) * 25000)
		                      .apply(np.round).astype(np.int))

	def _get_category_names(self, category):
		other_categories = [val + ' freq' for _, val \
		                    in self.term_doc_matrix._category_idx_store.items() \
		                    if val != category]
		all_categories = other_categories + [category + ' freq']
		return all_categories, other_categories

	def _get_coordinates_from_transform_and_jitter_frequencies(self,
	                                                           category,
	                                                           df,
	                                                           other_categories,
	                                                           transform):
		x_data_raw = transform(df[other_categories].sum(axis=1), df.index)
		y_data_raw = transform(df[category + ' freq'], df.index)
		x_data = self._add_jitter(x_data_raw)
		y_data = self._add_jitter(y_data_raw)
		return x_data, y_data

	def _add_jitter(self, vec):
		"""
		:param vec: array to jitter
		:return: array, jittered version of arrays
		"""
		if self.jitter == 0:
			return vec
		else:
			to_ret = vec + np.random.rand(1, len(vec))[0] * self.jitter
			return to_ret

	def _term_rank_score_and_frequency_df(self, all_categories, category, scores):
		term_ranker = self.term_ranker(self.term_doc_matrix)
		if self.use_non_text_features:
			term_ranker.use_non_text_features()
		df = term_ranker.get_ranks()
		if scores is None:
			scores = self._get_default_scores(category, df)
		# np.array(self.term_doc_matrix.get_rudder_scores(category))
		# df['category score'] = np.array(self.term_doc_matrix.get_rudder_scores(category))
		category_column_name = category + ' freq'
		df['category score'] = RudderScore.get_score(
			df[category_column_name],
			df[[c for c in df.columns if c != category_column_name]].sum(axis=1)
		)
		if self.term_significance is not None:
			df['p'] = get_p_vals(self.term_doc_matrix, category_column_name,
			                     self.term_significance)
		df['not category score'] = np.sqrt(2) - df['category score']
		df['color_scores'] = scores
		df = filter_bigrams_by_pmis(
			df[df[all_categories].sum(axis=1) > self.minimum_term_frequency],
			threshold_coef=self.pmi_threshold_coefficient
		)
		if self.filter_unigrams:
			df = filter_out_unigrams_that_only_occur_in_one_bigram(df)
		if len(df) == 0:
			raise NoWordMeetsTermFrequencyRequirementsError()
		df['category score rank'] = rankdata(df['category score'], method='ordinal')
		df['not category score rank'] = rankdata(df['not category score'], method='ordinal')
		if self.max_terms and self.max_terms < len(df):
			assert self.max_terms > 0
			df = self._limit_max_terms(category, df)
		df = df.reset_index()
		return df

	def _limit_max_terms(self, category, df):
		df['score'] = self._term_importance_ranks(category, df)
		df = df.ix[df.sort_values('score').iloc[:self.max_terms].index]
		return df[[c for c in df.columns if c != 'score']]

	def _get_default_scores(self, category, df):
		category_column_name = category + ' freq'
		cat_word_counts = df[category_column_name]
		not_cat_word_counts = df[[c for c in df.columns if c != category_column_name]].sum(axis=1)
		scores = ScaledFScore.get_scores(cat_word_counts, not_cat_word_counts)
		return scores

	def _term_importance_ranks(self, category, df):
		return np.array([df['category score rank'], df['not category score rank']]).min(axis=0)

	def draw(self,
	         category,
	         num_top_words_to_annotate=4,
	         words_to_annotate=[],
	         scores=None,
	         transform=percentile_alphabetical):
		'''Outdated.  MPLD3 drawing.

		Parameters
		----------
		category
		num_top_words_to_annotate
		words_to_annotate
		scores
		transform

		Returns
		-------
		pd.DataFrame, html of fgure
		'''
		try:
			import matplotlib.pyplot as plt
		except:
			raise Exception("matplotlib and mpld3 need to be installed to use this function.")
		try:
			from mpld3 import plugins, fig_to_html
		except:
			raise Exception("mpld3 need to be installed to use this function.")
		all_categories, other_categories = self._get_category_names(category)
		df = self._term_rank_score_and_frequency_df(all_categories, category, scores)
		x_data, y_data = self._get_coordinates_from_transform_and_jitter_frequencies \
			(category, df, other_categories, transform)
		df_to_annotate = df[(df['not category score rank'] <= num_top_words_to_annotate)
		                    | (df['category score rank'] <= num_top_words_to_annotate)
		                    | df['term'].isin(words_to_annotate)]
		words = list(df['term'])

		font = {'family': 'sans-serif',
		        'color': 'black',
		        'weight': 'normal',
		        'size': 'large'}

		fig, ax = plt.subplots()
		plt.figure(figsize=(10, 10))
		plt.gcf().subplots_adjust(bottom=0.2)
		plt.gcf().subplots_adjust(right=0.2)

		points = ax.scatter(x_data,
		                    y_data,
		                    c=-df['color_scores'],
		                    cmap='seismic',
		                    s=10,
		                    edgecolors='none',
		                    alpha=0.9)
		tooltip = plugins.PointHTMLTooltip(points,
		                                   ['<span id=a>%s</span>' % w for w in words],
		                                   css='#a {background-color: white;}')
		plugins.connect(fig, tooltip)
		ax.set_ylim([-.2, 1.2])
		ax.set_xlim([-.2, 1.2])
		ax.xaxis.set_ticks([0., 0.5, 1.])
		ax.yaxis.set_ticks([0., 0.5, 1.])
		ax.set_ylabel(category.title() + ' Frequency Percentile', fontdict=font, labelpad=20)
		ax.set_xlabel('Not ' + category.title() + ' Frequency Percentile', fontdict=font, labelpad=20)

		for i, row in df_to_annotate.iterrows():
			# alignment_criteria = row['category score rank'] < row['not category score rank']
			alignment_criteria = i % 2 == 0
			horizontalalignment = 'right' if alignment_criteria else 'left'
			verticalalignment = 'bottom' if alignment_criteria else 'top'
			term = row['term']
			ax.annotate(term,
			            (x_data[i], y_data[i]),
			            size=15,
			            horizontalalignment=horizontalalignment,
			            verticalalignment=verticalalignment,
			            )
		# texts.append(
		# ax.text(row['dem freq scaled'], row['rep freq scaled'], row['word'])
		# )
		# adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
		plt.show()
		return df, fig_to_html(fig)
