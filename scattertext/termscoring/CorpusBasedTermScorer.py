from abc import ABCMeta, abstractmethod

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import vstack
from future.utils import with_metaclass


class CorpusBasedTermScorer(with_metaclass(ABCMeta, object)):
	def __init__(self, corpus, *args, **kwargs):
		self.corpus = corpus
		self.category_names = corpus.get_categories()
		self.category_ids = corpus._y
		self.tdf = None
		self._set_scorer_args(**kwargs)

	@abstractmethod
	def _set_scorer_args(self, **kwargs):
		pass

	def set_categories(self, category_name,
	                   not_category_names=[],
	                   neutral_category_names=[]):
		'''
		Specify the category to score. Optionally, score against a specific set of categories.
		'''
		tdf = self.corpus.get_term_freq_df()
		d = {'cat': tdf[category_name + ' freq']}
		if not_category_names == []:
			not_category_names = [c + ' freq' for c in self.corpus.get_categories()
			                      if c != category_name]
		else:
			not_category_names = [c + ' freq' for c in not_category_names]
		d['ncat'] = tdf[not_category_names].sum(axis=1)
		if neutral_category_names == []:
			#neutral_category_names = [c + ' freq' for c in self.corpus.get_categories()
			#                          if c != category_name and c not in not_category_names]
			pass
		else:
			neutral_category_names = [c + ' freq' for c in neutral_category_names]
		for i, c in enumerate(neutral_category_names):
			d['neut%s' % (i)] = tdf[c]
		self.tdf = pd.DataFrame(d)
		self.category_name = category_name
		self.not_category_names = [c[:-5] for c in not_category_names]
		self.neutral_category_names = [c[:-5] for c in neutral_category_names]
		return self

	def get_t_statistics(self):
		'''
		In this case, parameters a and b aren't used, since this information is taken
		directly from the corpus categories.

		Returns
		-------

		'''

		X = self.corpus.get_term_doc_mat()
		cat_X = X[np.isin(self.corpus.get_category_names_by_row(),
		                  [self.category_name] + self.neutral_category_names), :]
		ncat_X = X[np.isin(self.corpus.get_category_names_by_row(),
		                   self.not_category_names + self.neutral_category_names), :]

		if len(self.neutral_category_names) > 0:
			neut_X = [np.isin(self.corpus.get_category_names_by_row(), self.neutral_category_names)]
			cat_X = vstack([cat_X, neut_X])
			ncat_X = vstack([ncat_X, neut_X])

		def sparse_var(X):
			Xc = X.copy()
			Xc.data **= 2
			return np.array(Xc.mean(axis=0) - np.power(X.mean(axis=0), 2))[0]

		mean_delta = np.array(cat_X.mean(axis=0) - ncat_X.mean(axis=0))[0]
		cat_var = sparse_var(cat_X)
		ncat_var = sparse_var(ncat_X)
		cat_n = cat_X.shape[0]
		ncat_n = ncat_X.shape[0]
		pooled_stderr = np.sqrt(cat_var / cat_n + ncat_var / ncat_n)

		tt = mean_delta / pooled_stderr

		# Use Satterthaite-Welch adjustment for degrees of freedom
		degs_of_freedom = (cat_var ** 2 / cat_n + ncat_var ** 2 / ncat_n) ** 2 / (
				(cat_var ** 2 / cat_n) ** 2 / (cat_n - 1)
				+ (ncat_var ** 2 / ncat_n) ** 2 / (ncat_n - 1)
		)

		only_in_neutral_mask = self.tdf[['cat', 'ncat']].sum(axis=1) == 0
		pvals = stats.t.sf(np.abs(tt), degs_of_freedom)
		tt[only_in_neutral_mask] = 0
		pvals[only_in_neutral_mask] = 0

		return tt, pvals

	@abstractmethod
	def get_scores(self, *args):
		'''
		Args are ignored

		Returns
		-------
		'''

	@abstractmethod
	def get_name(self):
		pass
