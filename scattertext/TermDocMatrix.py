import pkgutil
import re
import warnings
from io import StringIO

import numpy as np
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
from scipy.stats import hmean, fisher_exact, rankdata, norm
from sklearn.cross_validation import cross_val_predict
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import RidgeClassifierCV, LassoCV

from scattertext.CSRMatrixTools import delete_columns

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


class InvalidScalerException(Exception):
	pass


class TermDocMatrix:
	def __init__(self, X, y, term_idx_store, category_idx_store, unigram_frequency_path=None):
		'''
		:param X: csr_matrix term document matrix
		:param y: np.array category index array
		:param term_idx_store: IndexStore word index
		:param category_idx_store: IndexStore category name index
		'''
		self._X, self._y, self._term_idx_store, self._category_idx_store = \
			X, y, term_idx_store, category_idx_store
		self._unigram_frequency_path = unigram_frequency_path

	def get_categories(self):
		return self._category_idx_store.values()

	def get_num_docs(self):
		'''
		:return: int number of documents
		'''
		return len(self._y)

	def get_total_unigram_count(self):
		return self._get_corpus_unigram_freq(
			self.get_term_freq_df().sum(axis=1)
		).sum()

	def get_term_freq_df(self):
		'''
		:return: pd.DataFrame indexed on terms, with columns giving frequencies for each
		'''
		d = {'term': self._term_idx_store._i2val}
		for i, category in self._category_idx_store.items():
			d[category + ' freq'] = self._X[self._y == i].sum(axis=0).A1
		return pd.DataFrame(d).set_index('term')

	def remove_terms(self, terms):
		'''
		:param terms: list of terms to remove
		:return: TermDocMatrix : new object with terms removed.

		This procedure is non-desctructive.
		'''
		idx_to_delete_list = []
		for term in terms:
			if term not in self._term_idx_store:
				raise KeyError('Term %s not found' % (term))
			idx_to_delete_list.append(self._term_idx_store.getidx(term))
		new_term_idx_store = self._term_idx_store.batch_delete_idx(idx_to_delete_list)
		new_X = delete_columns(self._X, idx_to_delete_list)
		return TermDocMatrix(X=new_X,
		                     y=self._y,
		                     term_idx_store=new_term_idx_store,
		                     category_idx_store=self._category_idx_store,
		                     unigram_frequency_path=self._unigram_frequency_path)

	def get_posterior_mean_ratio_scores(self, category):
		'''
		:param category: str category name
		:return:
		'''
		return self._get_posterior_mean_ratio_from_category(category)

	def get_rudder_scores(self, category):
		'''
		:param category: str category name
		:return:
		'''
		category_percentiles = self._get_term_percentiles_in_category(category)
		not_category_percentiles = self._get_term_percentiles_not_in_category(category)
		rudder_scores = self._get_rudder_scores_for_percentile_pair(category_percentiles,
		                                                            not_category_percentiles)
		return rudder_scores

	def _get_posterior_mean_ratio_from_category(self, category):
		cat_word_counts, not_cat_word_counts = self._get_catetgory_and_non_category_word_counts(category)
		return self._get_posterior_mean_ratio_from_counts(cat_word_counts, not_cat_word_counts)

	def _get_posterior_mean_ratio_from_counts(self, cat_word_counts, not_cat_word_counts):
		cat_posterior_mean = self._get_posterior_mean_from_counts(cat_word_counts, not_cat_word_counts)
		not_cat_posterior_mean = self._get_posterior_mean_from_counts(not_cat_word_counts, cat_word_counts)
		return np.log(cat_posterior_mean / not_cat_posterior_mean) / np.log(2)

	def _get_posterior_mean_from_counts(self, cat_word_counts, not_cat_word_counts):
		a = cat_word_counts
		b = cat_word_counts.sum() - cat_word_counts
		beta = ((cat_word_counts.sum() + not_cat_word_counts.sum())
		        / (cat_word_counts + not_cat_word_counts) - 1)
		posterior_mean = (1. + a) / (1. + a + b + beta)
		return posterior_mean

	def get_logistic_regression_coefs_l2(self, category):
		'''
		:param category: str category name
		:return: tuple (coefficient array, accuracy, majority class baseline accuracy)
		'''
		y = self._get_mask_from_category(category)
		X = TfidfTransformer().fit_transform(self._X)
		clf = RidgeClassifierCV()
		clf.fit(X, y)
		y_hat = cross_val_predict(clf, X, y)
		acc, baseline = self._get_accuracy_and_baseline_accuracy(y, y_hat)
		return clf.coef_[0], acc, baseline

	def _get_accuracy_and_baseline_accuracy(self, y, y_hat):
		acc = sum(y_hat == y) * 1. / len(y)
		baseline = max([sum(y), len(y) - sum(y)]) * 1. / len(y)
		return acc, baseline

	def get_logistic_regression_coefs_l1(self, category):
		'''
		:param category: str category name
		:return: tuple (coefficient array, accuracy, majority class baseline accuracy)
		'''
		y = self._get_mask_from_category(category)
		y_continuous = self._get_continuous_version_boolean_y(y)
		X = TfidfTransformer().fit_transform(self._X)
		clf = LassoCV(alphas=[0.1, 0.5, 1, 5])
		clf.fit(X, y_continuous)
		y_hat = (cross_val_predict(clf, X, y_continuous) > 0)
		acc, baseline = self._get_accuracy_and_baseline_accuracy(y, y_hat)
		return clf.coef_, acc, baseline

	def _get_continuous_version_boolean_y(self, y_bool):
		return 1000 * (y_bool * 2. - 1)

	def get_scaled_f_scores(self,
	                        category,
	                        scaler_algo='normcdf',
	                        beta=1.):
		'''
		:param category: str category name
		:param scaler_algo: function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'
		:return: array of harmonic means of scaled P(word|category) and scaled P(category|word)
		'''
		assert beta > 0
		cat_word_counts, not_cat_word_counts = self._get_catetgory_and_non_category_word_counts(category)
		scores = self._get_scaled_f_score_from_counts(cat_word_counts, not_cat_word_counts, scaler_algo, beta)
		return np.array(scores)

	def _get_scaled_f_score_from_counts(self, cat_word_counts, not_cat_word_counts, scaler_algo, beta=1):
		scaler = self._get_scaler_function(scaler_algo)
		p_word_given_category = cat_word_counts.astype(np.float64) / cat_word_counts.sum()
		p_category_given_word = cat_word_counts.astype(np.float64) / (cat_word_counts + not_cat_word_counts)
		scores \
			= self._computer_harmoic_mean_of_probabilities_over_non_zero_in_category_count_terms(
			cat_word_counts, p_category_given_word, p_word_given_category, scaler
		)
		return scores

	def _computer_harmoic_mean_of_probabilities_over_non_zero_in_category_count_terms(self, cat_word_counts,
	                                                                                  p_category_given_word,
	                                                                                  p_word_given_category,
	                                                                                  scaler):
		df = pd.DataFrame({
			'cat_word_counts': cat_word_counts,
			'p_word_given_category': p_word_given_category,
			'p_category_given_word': p_category_given_word
		})
		df_with_count = df[df['cat_word_counts'] > 0]
		df_with_count['scale p_word_given_category'] = scaler(df_with_count['p_word_given_category'])
		df_with_count['scale p_category_given_word'] = scaler(df_with_count['p_category_given_word'])
		df['scale p_word_given_category'] = 0
		df.loc[df_with_count.index, 'scale p_word_given_category'] \
			= df_with_count['scale p_word_given_category']
		df['scale p_category_given_word'] = 0
		df.loc[df_with_count.index, 'scale p_category_given_word'] \
			= df_with_count['scale p_category_given_word']
		score = hmean([df_with_count['scale p_category_given_word'],
		               df_with_count['scale p_word_given_category']])
		df['score'] = 0
		df.loc[df_with_count.index, 'score'] = score
		return df['score']

	def _get_scaler_function(self, scaler_algo):
		scaler = None
		if scaler_algo == 'percentile':
			scaler = lambda x: norm.cdf(x, x.mean(), x.std())
		elif scaler_algo == 'normcdf':
			# scaler = lambda x: ECDF(x[cat_word_counts != 0])(x)
			scaler = lambda x: rankdata(x).astype(np.float64) / len(x)
		elif scaler_algo == 'none':
			scaler = lambda x: x
		else:
			raise InvalidScalerException("Invalid scaler alogrithm.  Must be either percentile or normcdf.")
		return scaler

	def get_fisher_scores(self, category):
		cat_word_counts, not_cat_word_counts = self._get_catetgory_and_non_category_word_counts(category)
		return self._get_fisher_scores_from_counts(cat_word_counts, not_cat_word_counts)

	def get_fisher_scores_vs_background(self):
		'''
		:return: pd.DataFrame of fisher scores vs background
		'''
		df = self._get_corpus_joined_to_background()
		odds_ratio, p_values = self._get_fisher_scores_from_counts(
			df['corpus'], df['background'])
		df['Odds ratio'] = odds_ratio
		df['Bonferroni-corrected p-values'] = p_values * len(df)
		df.sort_values(by=['Bonferroni-corrected p-values', 'Odds ratio'],
		               ascending=[True, False])
		return df

	def get_posterior_mean_ratio_scores_vs_background(self):
		'''
		:return: pd.DataFrame of posterior mean scores vs background
		'''
		df = self._get_corpus_joined_to_background()
		df['Log Posterior Mean Ratio'] = self._get_posterior_mean_ratio_from_counts(df['corpus'],
		                                                                            df['background'])
		return df.sort_values('Log Posterior Mean Ratio', ascending=False)

	def _get_catetgory_and_non_category_word_counts(self, category):
		cat_word_counts = self._X[self._get_mask_from_category(category)].sum(axis=0).A1
		not_cat_word_counts = self._X[self._y != self._category_idx_store.getidx(category)].sum(axis=0).A1
		return cat_word_counts, not_cat_word_counts

	def _get_fisher_scores_from_counts(self, cat_word_counts, not_cat_word_counts):
		cat_not_word_counts = cat_word_counts.sum() - cat_word_counts
		not_cat_not_word_counts = not_cat_word_counts.sum() - not_cat_word_counts

		def do_fisher_exact(x):
			return fisher_exact([[x[0], x[1]], [x[2], x[3]]], alternative='greater')

		odds_ratio, p_values = np.apply_along_axis(
			do_fisher_exact,
			0,
			np.array([cat_word_counts, cat_not_word_counts, not_cat_word_counts, not_cat_not_word_counts]))
		return odds_ratio, p_values

	def get_rudder_scores_vs_background(self):
		'''
		:return: pd.DataFrame of rudder scores vs background
		'''
		df = self._get_corpus_joined_to_background()
		corpus_percentiles = self._get_percentiles_from_freqs(df['corpus'])
		background_percentiles = self._get_percentiles_from_freqs(df['background'])
		df['Rudder'] = (self._get_rudder_scores_for_percentile_pair(corpus_percentiles,
		                                                            background_percentiles))
		df = df.sort_values(by='Rudder', ascending=True)
		return df

	def _rescale_labels_to_neg_one_pos_one(self, category):
		return (self._get_mask_from_category(category)) * 2 - 1

	def _get_corpus_joined_to_background(self):
		background_df = self._get_background_unigram_frequencies()
		term_freq_df = self.get_term_freq_df()
		corpus_freq_df = pd.DataFrame({'corpus': term_freq_df.sum(axis=1)})
		corpus_unigram_freq = self._get_corpus_unigram_freq(corpus_freq_df)
		df = corpus_unigram_freq.join(background_df, how='outer').fillna(0)
		return df

	def _get_corpus_unigram_freq(self, corpus_freq_df):
		unigram_validator = re.compile('^[A-Za-z]+$')
		corpus_unigram_freq = corpus_freq_df.ix[[term for term
		                                         in corpus_freq_df.index
		                                       if unigram_validator.match(term) is not None]]
		return corpus_unigram_freq

	def _get_background_unigram_frequencies(self):
		if self._unigram_frequency_path:
			unigram_freq_table_buf = open(self._unigram_frequency_path)
		else:
			unigram_freq_table_buf = StringIO(pkgutil.get_data('scattertext', 'data/count_1w.txt')
			                                  .decode('utf-8'))
		return (pd.read_table(unigram_freq_table_buf,
		                      names=['word', 'background'])
		        .set_index('word'))

	def get_scaled_f_score_scores_vs_background(self,
	                                            scaler_algo='none'):
		'''
		:param scaler_algo: see get_scaled_f_score_scores
		:return: returns dataframe of scaled_f_score scores compared to background corpus
		'''
		df = self._get_corpus_joined_to_background()
		df['Scaled f-score'] = self._get_scaled_f_score_from_counts(
			df['corpus'], df['background'], scaler_algo
		)
		return df.sort_values(by='Scaled f-score', ascending=False)

	def _get_rudder_scores_for_percentile_pair(self, category_percentiles, not_category_percentiles):
		return np.linalg.norm(np.array([1, 0])
		                      - np.array(list(zip(category_percentiles, not_category_percentiles))),
		                      axis=1)

	def _get_term_percentiles_in_category(self, category):
		mask = self._get_mask_from_category(category)
		return self._get_frequency_percentiles(mask)

	def _get_mask_from_category(self, category):
		return self._y == self._category_idx_store.getidx(category)

	def _get_term_percentiles_not_in_category(self, category):
		mask = self._y != self._category_idx_store.getidx(category)
		return self._get_frequency_percentiles(mask)

	def _get_frequency_percentiles(self, mask):
		freqs = self._X[mask].sum(axis=0).A1
		percentiles = self._get_percentiles_from_freqs(freqs)
		return percentiles

	def _get_percentiles_from_freqs(self, freqs):
		return rankdata(freqs) / len(freqs)
