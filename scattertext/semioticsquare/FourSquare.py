from scattertext import SemioticSquare
from scattertext.termranking import AbsoluteFrequencyRanker


class FourSquare(SemioticSquare):
	def __init__(self,
	             term_doc_matrix,
	             category_a_list,
	             category_b_list,
	             not_category_a_list,
	             not_category_b_list,
	             labels=None,
	             term_ranker=AbsoluteFrequencyRanker,
	             scorer=None):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			TermDocMatrix (or descendant) which will be used in constructing square.
		category_a_list : list
			Category names for term A
		category_b_list : list
			Category names for term B (in opposition to A)
		not_category_a_list : list
			List of category names that belong to not A
		not_category_b_list : list
			List of category names that belong to not A
		labels : dict
			None by default. Labels are dictionary of {'a_and_b': 'A and B', ...} to be shown
			above each category.
		term_ranker : TermRanker
			Class for returning a term-frequency convention_df
		scorer : termscoring class, optional
			Term scoring class for lexicon mining. Default: `scattertext.termscoring.ScaledFScore`
		'''

		self.category_a_list_ = category_a_list
		self.category_b_list_ = category_b_list
		self.not_category_a_list_ = not_category_a_list
		self.not_category_b_list_ = not_category_b_list
		assert (set(self._get_all_categories()) & set(term_doc_matrix.get_categories())
		        == set(self._get_all_categories()))
		self._build_square(term_doc_matrix, term_ranker, labels, scorer)

	def _get_x_axis(self, scorer, tdf):
		return scorer.get_scores(
			tdf[[t + ' freq' for t in set(self.category_a_list_ + self.not_category_b_list_)]].sum(axis=1),
			tdf[[t + ' freq' for t in set(self.category_b_list_ + self.not_category_a_list_)]].sum(axis=1)
		)

	def _get_y_axis(self, scorer, tdf):
		return scorer.get_scores(
			tdf[[t + ' freq' for t in set(self.category_a_list_ + self.category_b_list_)]].sum(axis=1),
			tdf[[t + ' freq' for t in set(self.not_category_b_list_ + self.not_category_a_list_)]].sum(axis=1)
		)

	def _get_all_categories(self):
		return (self.category_a_list_ + self.category_b_list_
		        + self.not_category_a_list_ + self.not_category_b_list_)

	def _get_default_a_label(self):
		return self.category_a_list_[0]

	def _get_default_b_label(self):
		return self.category_b_list_[0]

