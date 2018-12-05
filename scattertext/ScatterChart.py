import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from scattertext.PValGetter import get_p_vals
from scattertext.Scalers import percentile_min, percentile_alphabetical
from scattertext.ScatterChartData import ScatterChartData
from scattertext.TermDocMatrixFilter import filter_bigrams_by_pmis, \
	filter_out_unigrams_that_only_occur_in_one_bigram
from scattertext.termscoring import ScaledFScore
from scattertext.termscoring.CornerScore import CornerScore


class NoWordMeetsTermFrequencyRequirementsError(Exception):
	pass


class CoordinatesNotRightException(Exception): pass


class TermDocMatrixHasNoMetadataException(Exception): pass

def check_topic_model_string_format(term_dict):
	'''
	Parameters
	----------
	term_dict: dict {metadataname: [term1, term2, ....], ...}

	Returns
	-------
	None
	'''
	if type(term_dict) != dict:
		raise TypeError("Argument for term_dict must be a dict, keyed on strings, and contain a list of strings.")
	for k, v in term_dict.items():
		if type(v) != list:
			raise TypeError("Values in term dict must only be lists.")

		if sys.version_info[0] == 2:
			if type(k) != str and type(k) != unicode:
				raise TypeError("Keys in term dict must be of type str or unicode.")
			for e in v:
				if type(k) != str and type(k) != unicode:
					raise TypeError("Values in term lists must be str or unicode.")

		if sys.version_info[0] == 3:
			if type(k) != str:
				raise TypeError("Keys in term dict must be of type str.")
			for e in v:
				if type(e) != str:
					raise TypeError("Values in term lists must be str.")

class ScatterChart:
	def __init__(self,
	             term_doc_matrix,
	             **kwargs):
		'''
		Parameters
		----------
		term_doc_matrix: term document matrix to create chart from

		Remaining parameters are from ScatterChartData
		'''
		self.term_doc_matrix = term_doc_matrix
		self.scatterchartdata = ScatterChartData(**kwargs)
		self.x_coords = None
		self.y_coords = None
		self.original_x = None
		self.original_y = None
		self._rescale_x = None
		self._rescale_y = None
		self.used = False
		self.metadata_term_lists = None
		self.metadata_descriptions = None

	def inject_metadata_term_lists(self, term_dict):
		'''
		Inserts dictionary of meta data terms into object.

		Parameters
		----------
		term_dict: dict {metadataname: [term1, term2, ....], ...}

		Returns
		-------
		self: ScatterChart
		'''
		check_topic_model_string_format(term_dict)

		if not self.term_doc_matrix.metadata_in_use():
			raise TermDocMatrixHasNoMetadataException("No metadata is present in the term document matrix")

		self.metadata_term_lists = term_dict
		return self

	def inject_metadata_descriptions(self, term_dict):
		'''
		Inserts a set of descriptions of meta data terms.  These will be displayed
		below the scatter plot when a meta data term is clicked. All keys in the term dict
		must occur as meta data.

		Parameters
		----------
		term_dict: dict {metadataname: str: 'explanation to insert', ...}

		Returns
		-------
		self: ScatterChart
		'''
		assert type(term_dict) == dict
		if not self.term_doc_matrix.metadata_in_use():
			raise TermDocMatrixHasNoMetadataException("No metadata is present in the term document matrix")
		if set(term_dict.keys()) - set(self.term_doc_matrix.get_metadata()) != set():
			raise Exception('The following meta data terms are not present: '
							+ ', '.join(list(set(term_dict.keys()) - set(self.term_doc_matrix.get_metadata()))))

		if sys.version_info[0] == 2:
			assert set([type(v) for v in term_dict.values()]) - set([str, unicode]) == set()
		else:
			assert set([type(v) for v in term_dict.values()]) - set([str]) == set()


		self.metadata_descriptions = term_dict
		return self

	def inject_coordinates(self,
	                       x_coords,
	                       y_coords,
	                       rescale_x=None,
	                       rescale_y=None,
	                       original_x=None,
	                       original_y=None):
		'''
		Inject custom x and y coordinates for each term into chart.

		Parameters
		----------
		x_coords: array-like
			positions on x-axis \in [0,1]
		y_coords: array-like
			positions on y-axis \in [0,1]
		rescale_x: lambda list[0,1]: list[0,1], default identity
			Rescales x-axis after filtering
		rescale_y: lambda list[0,1]: list[0,1], default identity
			Rescales y-axis after filtering
		original_x : array-like, optional
			Original, unscaled x-values.  Defaults to x_coords
		original_y : array-like, optional
			Original, unscaled y-values.  Defaults to y_coords
		Returns
		-------
		self: ScatterChart

		'''
		self._verify_coordinates(x_coords, 'x')
		self._verify_coordinates(y_coords, 'y')
		self.x_coords = x_coords
		self.y_coords = y_coords
		self._rescale_x = rescale_x
		self._rescale_y = rescale_y
		self.original_x = x_coords if original_x is None else original_x
		self.original_y = y_coords if original_y is None else original_y

	def _verify_coordinates(self, coords, name):
		if self.scatterchartdata.use_non_text_features and len(coords) != len(self.term_doc_matrix.get_metadata()):
			raise CoordinatesNotRightException("Length of %s_cords must be the same as the number "
											   "of non-text features in the term_doc_matrix." % (name))
		if not self.scatterchartdata.use_non_text_features and len(coords) != self.term_doc_matrix.get_num_terms():
			raise CoordinatesNotRightException("Length of %s_cords must be the same as the number "
			                                   "of terms in the term_doc_matrix." % (name))
		if max(coords) > 1:
			raise CoordinatesNotRightException("Max value of %s_cords must be <= 1." % (name))
		if min(coords) < 0:
			raise CoordinatesNotRightException("Min value of %s_cords must be >= 0." % (name))

	def to_dict(self,
	            category,
	            category_name=None,
	            not_category_name=None,
	            scores=None,
	            transform=percentile_alphabetical,
	            title_case_names=False,
	            not_categories=None,
	            neutral_categories=None,
	            extra_categories=None,
	            background_scorer=None):
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
		title_case_names : bool, default False
		  Title case category name and no-category name?
		not_categories : list, optional
			List of categories to use as "not category".  Defaults to all others.
		neutral_categories : list, optional
			List of categories to use as neutral.  Defaults [].
		extra_categories : list, optional
			List of categories to use as extra.  Defaults [].
		background_scorer : CharacteristicScorer, optional
			Used for bg scores

		Returns
		-------
		Dictionary that encodes the scatter chart
		information. The dictionary can be dumped as a json document, and
		used in scattertext.html
		 {info: {category_name: ..., not_category_name},
		  data: [{term:,
		          x:frequency [0-1],
		          y:frequency [0-1],
		          ox: score,
		          oy: score,
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
		if self.used:
			raise Exception("Cannot reuse a ScatterChart constructor")

		all_categories = self.term_doc_matrix.get_categories()
		assert category in all_categories

		if not_categories is None:
			not_categories = [c for c in all_categories if c != category]
			neutral_categories = []
			extra_categories = []
		elif neutral_categories is None:
			neutral_categories = [c for c in all_categories
			                      if c not in [category] + not_categories]
			extra_categories = []
		elif extra_categories is None:
			extra_categories = [c for c in all_categories
			                    if c not in [category] + not_categories + neutral_categories]
		all_categories = [category] + not_categories + neutral_categories + extra_categories

		df = self._get_term_category_frequencies()

		if self.x_coords is not None:
			df['x'] = self.x_coords
			df['y'] = self.y_coords

		if not self.original_x is None:
			try:
				df['ox'] = self.original_x.values
			except AttributeError:
				df['ox'] = self.original_x

		if not self.original_y is None:
			try:
				df['oy'] = self.original_y.values
			except AttributeError:
				df['oy'] = self.original_y

		if scores is None:
			scores = self._get_default_scores(category, not_categories, df)
		category_column_name = category + ' freq'
		df['category score'] = CornerScore.get_scores_for_category(
			df[category_column_name],
			df[[c + ' freq' for c in not_categories]].sum(axis=1)
		)
		if self.scatterchartdata.term_significance is not None:
			df['p'] = get_p_vals(df, category_column_name,
			                     self.scatterchartdata.term_significance)
		df['not category score'] = CornerScore.get_scores_for_category(
			df[[c + ' freq' for c in not_categories]].sum(axis=1),
			df[category_column_name]
		)
		df['color_scores'] = scores
		if self.scatterchartdata.terms_to_include is None:
			df = self._filter_bigrams_by_minimum_not_category_term_freq(
				category_column_name, not_categories, df)
			df = filter_bigrams_by_pmis(
				self._filter_by_minimum_term_frequency(all_categories, df),
				threshold_coef=self.scatterchartdata.pmi_threshold_coefficient
			)

		if self.scatterchartdata.filter_unigrams:
			df = filter_out_unigrams_that_only_occur_in_one_bigram(df)
		if len(df) == 0:
			raise NoWordMeetsTermFrequencyRequirementsError()
		df['category score rank'] = rankdata(df['category score'], method='ordinal')
		df['not category score rank'] = rankdata(df['not category score'], method='ordinal')
		if self.scatterchartdata.max_terms and self.scatterchartdata.max_terms < len(df):
			assert self.scatterchartdata.max_terms > 0
			df = self._limit_max_terms(category, df)
		df = df.reset_index()

		if self.x_coords is None:
			self.x_coords, self.y_coords = self._get_coordinates_from_transform_and_jitter_frequencies \
				(category, df, not_categories, transform)
			df['x'], df['y'] = self.x_coords, self.y_coords
			df['ox'], df['oy'] = self.x_coords, self.y_coords

		df['not cat freq'] = df[[x + ' freq' for x in not_categories]].sum(axis=1)
		if neutral_categories != []:
			df['neut cat freq'] = df[[x + ' freq' for x in neutral_categories]].sum(axis=1).fillna(0)
		if extra_categories != []:
			df['extra cat freq'] = df[[x + ' freq' for x in extra_categories]].sum(axis=1).fillna(0)

		json_df = df[['x', 'y', 'ox', 'oy', 'term']]

		if self.scatterchartdata.term_significance:
			json_df['p'] = df['p']
		self._add_term_freq_to_json_df(json_df, df, category)
		json_df['s'] = percentile_min(df['color_scores'])
		json_df['os'] = df['color_scores']
		if background_scorer:
			bg_scores = background_scorer.get_scores(self.term_doc_matrix)
			json_df['bg'] = bg_scores[1].loc[json_df.term].values
		elif not self.scatterchartdata.use_non_text_features:
			json_df['bg'] = self._get_corpus_characteristic_scores(json_df)

		self._preform_axis_rescale(json_df, self._rescale_x, 'x')
		self._preform_axis_rescale(json_df, self._rescale_y, 'y')

		if self.scatterchartdata.terms_to_include is not None:
			json_df = self._use_only_selected_terms(json_df)

		category_terms = list(json_df.sort_values('s')['term'][:10])
		not_category_terms = list(json_df.sort_values('s')['term'][:10])
		if category_name is None:
			category_name = category
		if not_category_name is None:
			not_category_name = 'Not ' + category_name

		def better_title(x):
			if title_case_names:
				return ' '.join([t[0].upper() + t[1:].lower() for t in x.split()])
			else:
				return x

		j = {'info': {'category_name': better_title(category_name),
		              'not_category_name': better_title(not_category_name),
		              'category_terms': category_terms,
		              'not_category_terms': not_category_terms,
		              'category_internal_name': category,
		              'not_category_internal_names': not_categories,
		              'categories': self.term_doc_matrix.get_categories(),
		              'neutral_category_internal_names': neutral_categories,
		              'extra_category_internal_names': extra_categories}}
		if self.metadata_term_lists is not None:
			j['metalists'] = self.metadata_term_lists
		if self.metadata_descriptions is not None:
			j['metadescriptions'] = self.metadata_descriptions
		j['data'] = json_df.sort_values(by=['x', 'y', 'term']).to_dict(orient='records')
		return j

	def _get_term_category_frequencies(self):
		return self.term_doc_matrix.get_term_category_frequencies(self.scatterchartdata)

	def _use_only_selected_terms(self, json_df):
		term_df = pd.DataFrame({"term": self.scatterchartdata.terms_to_include})
		return pd.merge(json_df, term_df, on='term', how='inner')

	def _preform_axis_rescale(self, json_df, rescaler, variable_to_rescale):
		if rescaler is not None:
			json_df[variable_to_rescale] = rescaler(json_df[variable_to_rescale])
			assert json_df[variable_to_rescale].min() >= 0 and json_df[variable_to_rescale].max() <= 1

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
		if 'neut cat freq' in term_freq_df:
			json_df['neut25k'] = (((term_freq_df['neut cat freq'] * 1.
			                        / term_freq_df['neut cat freq'].sum()) * 25000)
			                      .apply(np.round).astype(np.int))
			json_df['neut'] = term_freq_df['neut cat freq']
		else:
			json_df['neut25k'] = 0
			json_df['neut'] = 0
		if 'extra cat freq' in term_freq_df:
			json_df['extra25k'] = (((term_freq_df['extra cat freq'] * 1.
			                         / term_freq_df['extra cat freq'].sum()) * 25000)
			                       .apply(np.round).astype(np.int))
			json_df['extra'] = term_freq_df['extra cat freq']
		else:
			json_df['extra25k'] = 0
			json_df['extra'] = 0

	def _get_category_names(self, category):
		other_categories = [val + ' freq' for val \
		                    in self.term_doc_matrix.get_categories() \
		                    if val != category]
		all_categories = other_categories + [category + ' freq']
		return all_categories, other_categories

	def _get_coordinates_from_transform_and_jitter_frequencies(self,
	                                                           category,
	                                                           df,
	                                                           other_categories,
	                                                           transform):
		not_counts = df[[c + ' freq' for c in other_categories]].sum(axis=1)
		counts = df[category + ' freq']
		x_data_raw = transform(not_counts, df.index, counts)
		y_data_raw = transform(counts, df.index, not_counts)
		x_data = self._add_jitter(x_data_raw)
		y_data = self._add_jitter(y_data_raw)
		return x_data, y_data

	def _add_jitter(self, vec):
		"""
		:param vec: array to jitter
		:return: array, jittered version of arrays
		"""
		if self.scatterchartdata.jitter == 0 or self.scatterchartdata.jitter is None:
			return vec
		return vec + np.random.rand(1, len(vec))[0] * self.scatterchartdata.jitter

	def _term_rank_score_and_frequency_df(self, all_categories, category, other_categories, scores):
		df = self._get_term_category_frequencies()
		if self.x_coords is not None:
			df['x'] = self.x_coords
			df['y'] = self.y_coords

		if not self.original_x is None:
			try:
				df['ox'] = self.original_x.values
			except AttributeError:
				df['ox'] = self.original_x

		if not self.original_y is None:
			try:
				df['oy'] = self.original_y.values
			except AttributeError:
				df['oy'] = self.original_y

		if scores is None:
			scores = self._get_default_scores(category, other_categories, df)
		# np.array(self.term_doc_matrix.get_rudder_scores(category))
		# convention_df['category score'] = np.array(self.term_doc_matrix.get_rudder_scores(category))
		category_column_name = category + ' freq'
		df['category score'] = CornerScore.get_scores_for_category(
			df[category_column_name],
			df[[c + ' freq' for c in other_categories]].sum(axis=1)
		)
		if self.scatterchartdata.term_significance is not None:
			df['p'] = get_p_vals(df, category_column_name,
			                     self.scatterchartdata.term_significance)
		df['not category score'] = CornerScore.get_scores_for_category(
			df[[c + ' freq' for c in other_categories]].sum(axis=1),
			df[category_column_name]
		)
		df['color_scores'] = scores
		if self.scatterchartdata.terms_to_include is None:
			df = self._filter_bigrams_by_minimum_not_category_term_freq(
				category_column_name, other_categories, df)
			df = filter_bigrams_by_pmis(
				self._filter_by_minimum_term_frequency(all_categories, df),
				threshold_coef=self.scatterchartdata.pmi_threshold_coefficient
			)

		if self.scatterchartdata.filter_unigrams:
			df = filter_out_unigrams_that_only_occur_in_one_bigram(df)
		if len(df) == 0:
			raise NoWordMeetsTermFrequencyRequirementsError()
		df['category score rank'] = rankdata(df['category score'], method='ordinal')
		df['not category score rank'] = rankdata(df['not category score'], method='ordinal')
		if self.scatterchartdata.max_terms and self.scatterchartdata.max_terms < len(df):
			assert self.scatterchartdata.max_terms > 0
			df = self._limit_max_terms(category, df)
		df = df.reset_index()
		return df

	def _filter_bigrams_by_minimum_not_category_term_freq(self, category_column_name, other_categories, df):
		if self.scatterchartdata.terms_to_include is None:
			return df[(df[category_column_name] > 0)
			          | (df[[c + ' freq' for c in other_categories]].sum(axis=1)
			             >= self.scatterchartdata.minimum_not_category_term_frequency)]
		else:
			return df

	def _filter_by_minimum_term_frequency(self, all_categories, df):
		if self.scatterchartdata.terms_to_include is None:
			return df[df[[c + ' freq' for c in all_categories]].sum(axis=1)
			          > self.scatterchartdata.minimum_term_frequency]
		else:
			return df

	def _limit_max_terms(self, category, df):
		df['score'] = self._term_importance_ranks(category, df)
		df = df.ix[df.sort_values('score').iloc[:self.scatterchartdata.max_terms].index]
		return df[[c for c in df.columns if c != 'score']]

	def _get_default_scores(self, category, other_categories, df):
		category_column_name = category + ' freq'
		cat_word_counts = df[category_column_name]
		not_cat_word_counts = df[[c + ' freq' for c in other_categories]].sum(axis=1)
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
		df = self._term_rank_score_and_frequency_df(all_categories, category, other_categories, scores)
		if self.x_coords is None:
			df['x'], df['y'] = self._get_coordinates_from_transform_and_jitter_frequencies \
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

		points = ax.scatter(self.x_coords,
		                    self.y_coords,
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
			            (self.x_coords[i], y_data[i]),
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
