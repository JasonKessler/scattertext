import numpy as np

from scattertext.semioticsquare import SemioticSquare
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference


class FourSquareAxes(SemioticSquare):
	'''
	This creates a semiotic square where the complex term is considered the "top" category, the
	neutral term is the "bottom" category, the positive dexis is the "left" category, and the
	negative dexis is the "right" category.
	'''
	def __init__(self,
	             term_doc_matrix,
	             left_categories,
	             right_categories,
	             top_categories,
	             bottom_categories,
	             left_category_name=None,
	             right_category_name=None,
	             top_category_name=None,
	             bottom_category_name=None,
	             x_scorer=RankDifference(),
	             y_scorer=RankDifference(),
	             term_ranker=AbsoluteFrequencyRanker,
	             labels=None):
		for param in [left_categories, right_categories, top_categories, bottom_categories]:
			assert type(param) == list
			assert set(param) - set(term_doc_matrix.get_categories()) == set()
			assert len(param) > 0
		self.term_doc_matrix_ = term_doc_matrix
		self._labels = labels
		self.left_category_name_ = left_category_name if left_category_name is not None else left_categories[0]
		self.right_category_name_ = right_category_name if right_category_name is not None else right_categories[0]
		self.top_category_name_ = top_category_name if top_category_name is not None else top_categories[0]
		self.bottom_category_name_ = bottom_category_name if bottom_category_name is not None else bottom_categories[0]
		self.x_scorer_ = x_scorer
		self.y_scorer_ = y_scorer
		self.term_ranker_ = term_ranker
		self.left_categories_, self.right_categories_, self.top_categories_, self.bottom_categories_ \
			= left_categories, right_categories, top_categories, bottom_categories
		self.axes = self._build_axes()
		self.lexicons = self._build_lexicons()

	def _get_y_baseline(self):
		return self.y_scorer_.get_default_score()

	def _get_x_baseline(self):
		return self.x_scorer_.get_default_score()

	def _get_all_categories(self):
		return self.left_categories_ + self.right_categories_ + self.top_categories_ + self.bottom_categories_

	def _build_axes(self, scorer=None):
		tdf = self.term_ranker_(self.term_doc_matrix_).get_ranks()
		tdf.columns = [c[:-5] for c in tdf.columns]

		tdf = tdf[self._get_all_categories()]
		counts = tdf.sum(axis=1)
		tdf['x'] = self.x_scorer_.get_scores(tdf[self.left_categories_].sum(axis=1),
		                                     tdf[self.right_categories_].sum(axis=1))
		tdf['x'][np.isnan(tdf['x'])] = self.x_scorer_.get_default_score()
		tdf['y'] = self.y_scorer_.get_scores(tdf[self.top_categories_].sum(axis=1),
		                                     tdf[self.bottom_categories_].sum(axis=1))
		tdf['y'][np.isnan(tdf['y'])] = self.y_scorer_.get_default_score()
		tdf['counts'] = counts
		return tdf[['x', 'y', 'counts']]

	def get_labels(self):
		a = self._get_default_a_label()
		b = self._get_default_b_label()
		default_labels = {'a': a,
		                  'not_a': '' if a == '' else 'Not ' + a,
		                  'b': b,
		                  'not_b': '' if b == '' else 'Not ' + b,
		                  'a_and_b': self.top_category_name_,
		                  'not_a_and_not_b': self.bottom_category_name_,
		                  'a_and_not_b': self.left_category_name_,
		                  'b_and_not_a': self.right_category_name_}
		labels = self._labels
		if labels is None:
			labels = {}
		return {name + '_label': labels.get(name, default_labels[name])
		        for name in default_labels}

	def _get_default_b_label(self):
		return ''

	def _get_default_a_label(self):
		return ''
