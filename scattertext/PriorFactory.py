import pandas as pd
import numpy as np

from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termsignificance.LogOddsRatioInformativeDirichletPiror import LogOddsRatioInformativeDirichletPrior


class PriorFactory(object):
	def __init__(self,
	             term_doc_mat,
	             category=None,
	             not_categories=None,
	             starting_count=0.0001,
	             term_ranker=AbsoluteFrequencyRanker):
		'''
		Parameters
		----------
		term_doc_mat : TermDocMatrix
			Basis for scores
		category : str
			Category to score. Only important when finding neutral categories.
		not_categories : list
		  List of categories to score against.  If None (the default) the list
		   is the remaining
		starting_count : float
			Default 0.01. Add this count to each term seen. If zero, terms not in background counts will be removed.
		term_ranker : TermRanker
			Function to get term frequency convention_df
		'''
		self.term_doc_mat = term_doc_mat
		self.relevant_categories = []
		if category:
			self.category = category
			assert category in term_doc_mat.get_categories()
			self.relevant_categories += [category]
		else:
			self.category = None
		if not_categories == None:
			not_categories = [c for c in term_doc_mat.get_categories()
			                  if c != category]
		else:
			assert set(not_categories) - set(term_doc_mat.get_categories()) == set()
		self.relevant_categories += not_categories
		self.not_categories = not_categories
		self.starting_count = starting_count
		self.term_ranker = term_ranker(term_doc_mat)
		self.use_preset_term_frequencies = False
		self.priors = pd.Series(np.zeros(len(self.term_doc_mat.get_terms())),
		                        index=term_doc_mat.get_terms())

	def use_general_term_frequencies(self):
		'''
		Returns
		-------
		PriorFactory
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
			'corpus': self.term_ranker.get_ranks()
			[[c + ' freq' for c in self.relevant_categories]]
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
		PriorFactory
		'''
		self.priors += custom_term_frequencies.reindex(self.priors.index).fillna(0)
		return self

	def use_categories(self, categories):
		self.priors += self.term_ranker.get_ranks()[
			[c + ' freq' for c in categories]].sum(axis=1)
		return self

	def use_all_categories(self):
		'''
		Returns
		-------
		PriorFactory
		'''
		term_df = self.term_ranker.get_ranks()
		self.priors += term_df.sum(axis=1).fillna(0.)
		return self

	def use_neutral_categories(self):
		'''
		Returns
		-------
		PriorFactory
		'''
		term_df = self.term_ranker.get_ranks()
		self.priors += term_df[[c + ' freq' for c in self._get_neutral_categories()]].sum(axis=1)
		return self

	def drop_neutral_categories_from_corpus(self):
		'''
		Returns
		-------
		PriorFactory
		'''
		neutral_categories = self._get_neutral_categories()
		self.term_doc_mat = self.term_doc_mat.remove_categories(neutral_categories)
		self._reindex_priors()
		return self

	def _get_neutral_categories(self):
		return [c for c in self.term_doc_mat.get_categories()
		        if c not in self.relevant_categories]

	def _reindex_priors(self):
		self.priors = self.priors.reindex(self.term_doc_mat.get_terms()).dropna()

	def drop_unused_terms(self):
		'''
		Returns
		-------
		PriorFactory
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
		PriorFactory
		'''
		self.term_doc_mat = self.term_doc_mat.remove_terms(
			self.priors[self.priors == 0].index
		)
		self._reindex_priors()
		return self

	def align_to_target(self, target_term_doc_mat):
		'''
		Parameters
		----------
		target_term_doc_mat : TermDocMatrix

		Returns
		-------
		PriorFactory
		'''
		self.priors = self.priors[target_term_doc_mat.get_terms()].fillna(0)
		return self

	def build(self):
		'''
		Returns
		-------
		pd.Series, TermDocMatrix
		'''
		return self.get_priors(), self.term_doc_mat

	def get_priors(self):
		'''
		Returns
		-------
		pd.Series
		'''
		priors = self.priors
		priors[~np.isfinite(priors)] = 0
		priors += self.starting_count
		return priors
