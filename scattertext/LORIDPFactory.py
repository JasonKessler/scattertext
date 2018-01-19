import pandas as pd

from scattertext.termsignificance.LogOddsRatioInformativeDirichletPiror import LogOddsRatioInformativeDirichletPrior


class LORIDPFactory(object):
	def __init__(self,
	             term_doc_mat,
	             category,
	             not_categories=None,
	             alpha=1,
	             starting_count=0.0001,
	             term_freq_df_func=lambda x: x.get_term_freq_df()):
		'''
		Parameters
		----------
		term_doc_mat : TermDocMatrix
			Basis for scores
		category : str
			Category to score
		not_categories : list
		  List of categories to score against.  If None (the default) the list
		   is the remaining
		alpha : float
			Default 1. Size to scale background word counts relative to n.
		starting_count : float
			Default 0.01. Add this count to each term seen. If zero, terms not in background counts will be removed.
		term_freq_df_func : lambda (corpus)
			Function to get term frequency df
		'''
		self.term_doc_mat = term_doc_mat
		self.category = category
		assert category in term_doc_mat.get_categories()
		if not_categories == None:
			not_categories = [c for c in term_doc_mat.get_categories()
			                  if c != category]
		else:
			assert set(not_categories) - set(term_doc_mat.get_categories()) == set()
		self.not_categories = not_categories
		self.alpha = alpha
		self.starting_count = starting_count
		self.term_freq_df_func = term_freq_df_func
		self.use_preset_term_frequencies = False
		tdf = self._get_relevant_term_freq()
		self.priors = tdf.corpus
		self.priors[:] = 0.

	def use_general_term_frequencies(self):
		'''
		Returns
		-------
		self
		'''
		tdf = self._get_relevant_term_freq()
		bg_df = self.term_doc_mat.get_term_and_background_counts()[['background']]
		bg_df = pd.merge(tdf,
		                 bg_df,
		                 left_index=True,
		                 right_index=True,
		                 how='left').fillna(0.)
		self._store_priors_from_background_dataframe(bg_df)
		return self

	def _get_relevant_term_freq(self):
		return pd.DataFrame({
			'corpus': self.term_freq_df_func(self.term_doc_mat)
			[[c + ' freq' for c in [self.category] + self.not_categories]]
				.sum(axis=1)
		})

	def _store_priors_from_background_dataframe(self, bg_df):
		self.priors += bg_df.reindex(self.priors.index).fillna(0)['background']

	def use_custom_term_frequencies(self, custom_term_frequencies):
		'''
		Parameters
		----------
		pd.Series
		term -> frequency
		Returns
		-------
		LORIDPFactory
		'''
		self.priors += custom_term_frequencies.reindex(self.priors.index).fillna(0)
		return self

	def use_all_categories(self):
		'''
		Returns
		-------
		LORIDPFactory
		'''
		term_df = self.term_freq_df_func(self.term_doc_mat)
		self.priors += term_df.sum(axis=1).fillna(0.)
		return self

	def use_neutral_categories(self):
		'''
		Returns
		-------
		LORIDPFactory
		'''
		term_df = self.term_freq_df_func(self.term_doc_mat)
		self.priors += term_df[[c + ' freq' for c in self._get_neutral_categories()]].sum(axis=1)
		return self

	def drop_neutral_categories_from_corpus(self):
		'''
		Returns
		-------
		LORIDPFactory
		'''
		neutral_categories = self._get_neutral_categories()
		self.term_doc_mat = self.term_doc_mat.remove_categories(neutral_categories)
		self._reindex_priors()
		return self

	def _get_neutral_categories(self):
		return [c for c in self.term_doc_mat.get_categories()
		        if c != self.category and c not in self.not_categories]

	def _reindex_priors(self):
		self.priors = self.priors.reindex(self.term_doc_mat.get_terms()).dropna()

	def drop_unused_terms(self):
		'''
		Returns
		-------
		LORIDPFactory
		'''
		self.term_doc_mat = self.term_doc_mat.remove_terms(
			set(self.term_doc_mat.get_terms()) - set(self.priors.index)
		)
		self._reindex_priors()
		return self

	def drop_zero_priors(self):
		'''
		Returns
		-------
		LORIDPFactory
		'''
		self.term_doc_mat = self.term_doc_mat.remove_terms(
			self.priors[self.priors == 0].index
		)
		self._reindex_priors()
		return self

	def build(self):
		'''
		Returns
		-------
		LogOddsRatioInformativeDirichletPrior, TermDocMatrix
		'''
		return self.get_term_scorer(), self.term_doc_mat

	def get_term_scorer(self):
		'''
		Returns
		-------
		LogOddsRatioInformativeDirichletPrior
		'''
		return LogOddsRatioInformativeDirichletPrior(self.priors + self.starting_count, self.alpha)
