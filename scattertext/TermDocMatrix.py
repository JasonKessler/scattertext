import pkgutil
import re
import warnings
from io import StringIO

import numpy as np
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
from scipy.sparse import csr_matrix
from scipy.stats import hmean, fisher_exact, rankdata, norm
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifierCV, LassoCV

from scattertext.CSRMatrixTools import delete_columns
from scattertext.FeatureOuput import FeatureLister

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

from scattertext.termscoring.ScaledFScore import InvalidScalerException

SPACY_ENTITY_TAGS = ['person', 'norp', 'facility', 'org', 'gpe',
                     'loc', 'product', 'event', 'work_of_art', 'language',
                     'type', 'date', 'time', 'percent', 'money', 'quantity',
                     'ordinal', 'cardinal']


class TermDocMatrix(object):
	'''
	!!! to do: refactor score functions into classes
	'''

	def __init__(self,
	             X, mX, y,
	             term_idx_store,
	             category_idx_store,
	             metadata_idx_store,
	             unigram_frequency_path=None):
		'''

		Parameters
		----------
		X : csr_matrix
			term document matrix
		mX : csr_matrix
			metadata-document matrix
		y : np.array
			category index array
		term_idx_store : IndexStore
			Term indices
		category_idx_store : IndexStore
			Catgory indices
		metadata_idx : IndexStore
		  Document metadata indices
		unigram_frequency_path : str or None
			Path to term frequency file.
		'''
		self._X, self._mX, self._y, self._term_idx_store, self._category_idx_store = \
			X, mX, y, term_idx_store, category_idx_store
		self._metadata_idx_store = metadata_idx_store
		self._unigram_frequency_path = unigram_frequency_path
		self._background_corpus = None

	def get_num_terms(self):
		'''
		Returns
		-------
		The number of terms registered in the term doc matrix
		'''
		return len(self._term_idx_store)

	def get_categories(self):
		'''

		Returns
		-------
		list
		Category names
		'''
		return self._category_idx_store.values()

	def get_num_docs(self):
		'''

		Returns
		-------
		int, number of documents
		'''
		return len(self._y)

	def get_total_unigram_count(self):
		return self._get_unigram_term_freq_df().sum()

	def _get_unigram_term_freq_df(self):
		return self._get_corpus_unigram_freq(
			self.get_term_freq_df().sum(axis=1)
		)

	def old_get_term_freq_df(self):
		d = {'term': self._term_idx_store._i2val}
		for i, category in self._category_idx_store.items():
			d[category + ' freq'] = self._X[self._y == i].sum(axis=0).A1
		return pd.DataFrame(d).set_index('term')

	def get_term_freq_df(self):
		'''

		Returns
		-------
		pd.DataFrame indexed on terms, with columns giving frequencies for each
		'''
		row = self._row_category_ids()
		newX = csr_matrix((self._X.data, (row, self._X.indices)))
		return self._term_freq_df_from_matrix(newX)

	def _term_freq_df_from_matrix(self, catX):
		return self._get_freq_df_using_idx_store(catX, self._term_idx_store)

	def _get_freq_df_using_idx_store(self, catX, idx_store):
		d = {'term': idx_store._i2val}
		for idx, cat in self._category_idx_store.items():
			d[cat + ' freq'] = catX[idx, :].A[0]
		return pd.DataFrame(d).set_index('term')

	def get_metadata_freq_df(self):
		'''
		Returns
		-------
		pd.DataFrame indexed on metadata, with columns giving frequencies for each
		'''
		row = self._row_category_ids_for_meta()
		newX = csr_matrix((self._mX.data, (row, self._mX.indices)))
		return self._metadata_freq_df_from_matrix(newX)

	def _row_category_ids(self):
		row = self._X.tocoo().row
		for i, cat in enumerate(self._y):
			row[row == i] = cat
		return row

	def _row_category_ids_for_meta(self):
		row = self._mX.tocoo().row
		for i, cat in enumerate(self._y):
			row[row == i] = cat
		return row

	def _metadata_freq_df_from_matrix(self, catX):
		return self._get_freq_df_using_idx_store(catX, self._metadata_idx_store)

	def get_category_names_by_row(self):
		'''
		Returns
		-------
		np.array of the category name for each row
		'''
		return np.array(self.get_categories())[self._y]

	def get_unigram_corpus(self):
		'''
		Returns
		-------
		A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
		'''
		terms_to_ignore = [term for term
		                   in self._term_idx_store._i2val
		                   if ' ' in term or "'" in term]
		return self.remove_terms(terms_to_ignore)

	def remove_entity_tags(self):
		'''
		Returns
		-------
		A new TermDocumentMatrix consisting of only terms in the current TermDocumentMatrix
		 that aren't spaCy entity tags.

		Note: Used if entity types are censored using FeatsFromSpacyDoc(tag_types_to_censor=...).
		'''
		terms_to_remove = [term for term in self._term_idx_store._i2val
		                   if any([word in SPACY_ENTITY_TAGS for word in term.split()])]
		return self.remove_terms(terms_to_remove)

	def get_stoplisted_unigram_corpus(self, stoplist=None):
		'''
		Parameters
		-------
		stoplist : list, optional

		Returns
		-------
		A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
		'''
		if stoplist is None:
			stoplist = ENGLISH_STOP_WORDS
		else:
			stoplist = [w.lower() for w in stoplist]
		return self._remove_terms_from_list(stoplist)

	def get_stoplisted_unigram_corpus_and_custom(self,
	                                             custom_stoplist):
		'''
		Parameters
		-------
		stoplist : list of lower-cased words, optional

		Returns
		-------
		A new TermDocumentMatrix consisting of only unigrams in the current TermDocumentMatrix.
		'''
		if type(custom_stoplist) == str:
			custom_stoplist = [custom_stoplist]
		return self._remove_terms_from_list(set(ENGLISH_STOP_WORDS)
		                                    | set(w.lower() for w in custom_stoplist))

	def _remove_terms_from_list(self, stoplist):
		terms_to_ignore = [term for term
		                   in self._term_idx_store._i2val
		                   if ' ' in term or "'" in term
		                   or term in stoplist]
		return self.remove_terms(terms_to_ignore)

	def term_doc_lists(self):
		'''
		Returns
		-------
		dict
		'''
		doc_ids = self._X.transpose().tolil().rows
		terms = self._term_idx_store.values()
		return dict(zip(terms, doc_ids))

	def get_term_doc_count_df(self):
		'''

		Returns
		-------
		pd.DataFrame indexed on terms, with columns giving the
		 number of docs containing each term
		'''
		row = self._row_category_ids()
		catX = self._change_document_type_in_matrix(self._X, row)
		return self._term_freq_df_from_matrix(catX)

	def _change_document_type_in_matrix(self, X, new_doc_ids):
		new_data = self._make_all_positive_data_ones(X.data)
		newX = csr_matrix((new_data, (new_doc_ids, X.indices)))
		return newX

	def _make_all_positive_data_ones(self, newX):
		# type: (sparse_matrix) -> sparse_matrix
		return (newX > 0).astype(np.int32)

	def remove_terms(self, terms, ignore_absences=False):
		'''Non destructive term removal.

		Parameters
		----------
		terms : list
			list of terms to remove
		ignore_absences : bool, False by default
			if term does not appear, don't raise an error, just move on.

		Returns
		-------
		TermDocMatrix, new object with terms removed.
		'''
		idx_to_delete_list = []
		for term in terms:
			if term not in self._term_idx_store:
				if not ignore_absences:
					raise KeyError('Term %s not found' % (term))
				continue
			idx_to_delete_list.append(self._term_idx_store.getidx(term))
		return self.remove_terms_by_indices(idx_to_delete_list)

	def remove_terms_by_indices(self, idx_to_delete_list):
		new_term_idx_store = self._term_idx_store.batch_delete_idx(idx_to_delete_list)
		new_X = delete_columns(self._X, idx_to_delete_list)
		return self._term_doc_matrix_with_new_X(new_X, new_term_idx_store)

	def _term_doc_matrix_with_new_X(self, new_X, new_term_idx_store):
		return TermDocMatrix(X=new_X,
		                     mX=self._mX,
		                     y=self._y,
		                     term_idx_store=new_term_idx_store,
		                     category_idx_store=self._category_idx_store,
		                     metadata_idx_store=self._metadata_idx_store,
		                     unigram_frequency_path=self._unigram_frequency_path)

	def get_posterior_mean_ratio_scores(self, category):
		''' Computes posterior mean score.
		Parameters
		----------
		category : str
			category name to score

		Returns
		-------
			np.array
		'''
		return self._get_posterior_mean_ratio_from_category(category)

	def get_rudder_scores(self, category):
		''' Computes Rudder score.
		Parameters
		----------
		category : str
			category name to score

		Returns
		-------
			np.array
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

	def get_logistic_regression_coefs_l2(self, category,
	                                     clf=RidgeClassifierCV()):
		''' Computes l2-penalized logistic regression score.
		Parameters
		----------
		category : str
			category name to score

		category : str
			category name to score
		Returns
		-------
			(coefficient array, accuracy, majority class baseline accuracy)
		'''
		from sklearn.cross_validation import cross_val_predict
		y = self._get_mask_from_category(category)
		X = TfidfTransformer().fit_transform(self._X)
		clf.fit(X, y)
		y_hat = cross_val_predict(clf, X, y)
		acc, baseline = self._get_accuracy_and_baseline_accuracy(y, y_hat)
		return clf.coef_[0], acc, baseline

	def _get_accuracy_and_baseline_accuracy(self, y, y_hat):
		acc = sum(y_hat == y) * 1. / len(y)
		baseline = max([sum(y), len(y) - sum(y)]) * 1. / len(y)
		return acc, baseline

	def get_logistic_regression_coefs_l1(self, category,
	                                     clf=LassoCV(alphas=[0.1, 0.001],
	                                                 max_iter=10000,
	                                                 n_jobs=-1)):
		''' Computes l1-penalized logistic regression score.
		Parameters
		----------
		category : str
			category name to score

		Returns
		-------
			(coefficient array, accuracy, majority class baseline accuracy)
		'''
		from sklearn.cross_validation import cross_val_predict
		y = self._get_mask_from_category(category)
		y_continuous = self._get_continuous_version_boolean_y(y)
		# X = TfidfTransformer().fit_transform(self._X)
		X = self._X

		clf.fit(X, y_continuous)
		y_hat = (cross_val_predict(clf, X, y_continuous) > 0)
		acc, baseline = self._get_accuracy_and_baseline_accuracy(y, y_hat)
		clf.fit(X, y_continuous)
		return clf.coef_, acc, baseline

	def get_regression_coefs(self, category, clf=ElasticNet()):
		''' Computes regression score of tdfidf transformed features
		Parameters
		----------
		category : str
			category name to score
		clf : sklearn regressor

		Returns
		-------
		coefficient array
		'''
		self._fit_tfidf_model(category, clf)
		return clf.coef_

	def get_logreg_coefs(self, category, clf=LogisticRegression()):
		''' Computes regression score of tdfidf transformed features
		Parameters
		----------
		category : str
			category name to score
		clf : sklearn regressor

		Returns
		-------
		coefficient array
		'''
		self._fit_tfidf_model(category, clf)
		return clf.coef_[0]

	def _fit_tfidf_model(self, category, clf):
		y = self._get_mask_from_category(category)
		y_continuous = self._get_continuous_version_boolean_y(y)
		X = TfidfTransformer().fit_transform(self._X)
		clf.fit(X, y_continuous)

	def _get_continuous_version_boolean_y(self, y_bool):
		return 1000 * (y_bool * 2. - 1)

	def get_scaled_f_scores(self,
	                        category,
	                        scaler_algo='normcdf',
	                        beta=1.):
		''' Computes scaled-fscores
		Parameters
		----------
		category : str
			category name to score
		scaler_algo : str
		  Function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'. Default normcdf
		beta : float
			Beta in (1+B^2) * (Scale(P(w|c)) * Scale(P(c|w)))/(B^2*Scale(P(w|c)) + Scale(P(c|w))). Defaults to 1.
		Returns
		-------
			np.array of harmonic means of scaled P(word|category) and scaled P(category|word)
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

	def _computer_harmoic_mean_of_probabilities_over_non_zero_in_category_count_terms(self,
	                                                                                  cat_word_counts,
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
		df.loc[df_with_count.index, 'scale p_word_given_category'] = df_with_count['scale p_word_given_category']
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
		Returns
		-------
			pd.DataFrame of fisher scores vs background
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
		Returns
		-------
			pd.DataFrame of posterior mean  scores vs background
		'''
		df = self._get_corpus_joined_to_background()
		df['Log Posterior Mean Ratio'] = self._get_posterior_mean_ratio_from_counts(df['corpus'],
		                                                                            df['background'])
		return df.sort_values('Log Posterior Mean Ratio', ascending=False)

	def _get_catetgory_and_non_category_word_counts(self, category):
		self._validate_category(category)
		cat_word_counts = self._X[self._get_mask_from_category(category)].sum(axis=0).A1
		not_cat_word_counts = self._X[self._y != self._category_idx_store.getidx(category)].sum(axis=0).A1
		return cat_word_counts, not_cat_word_counts

	def _validate_category(self, category):
		if category not in self.get_categories():
			raise Exception("Invalid category: %s, valid: %s" % (category, self.get_categories()))

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
		Returns
		-------
    pd.DataFrame of rudder scores vs background
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

	def set_background_corpus(self, background):
		'''
		Parameters
		----------
		background

		'''
		if issubclass(type(background), TermDocMatrix):
			self._background_corpus = pd.DataFrame(background
			                                       .get_term_freq_df()
			                                       .sum(axis=1),
			                                       columns=['background']).reset_index()
			self._background_corpus.columns = ['word', 'background']
		elif (type(background) == pd.DataFrame
		      and set(background.columns) == set(['word', 'background'])):
			self._background_corpus = background
		else:
			raise Exception('The argument named background must be a subclass of TermDocMatrix or a ' \
			                + 'DataFrame with columns "word" and "background", where "word" ' \
			                + 'is the term text, and "background" is its frequency.')

	def get_background_corpus(self):
		if self._background_corpus is not None:
			return self._background_corpus
		return None

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
		if self.get_background_corpus() is not None:
			return self.get_background_corpus()
		if self._unigram_frequency_path:
			unigram_freq_table_buf = open(self._unigram_frequency_path)
		else:
			unigram_freq_table_buf = StringIO(pkgutil.get_data('scattertext', 'data/count_1w.txt')
			                                  .decode('utf-8'))
		return (pd.read_table(unigram_freq_table_buf,
		                      names=['word', 'background'])
		        .sort_values(ascending=False, by='background')
		        .drop_duplicates(['word'])
		        .set_index('word'))

	def list_extra_features(self):
		'''
		Returns
		-------
		List of dicts.  One dict for each document, keys are metadata, values are counts
		'''
		return FeatureLister(self._mX,
		                     self._metadata_idx_store,
		                     self.get_num_docs()).output()

	def get_scaled_f_scores_vs_background(self, scaler_algo='none'):
		'''
		Parameters
		----------
		scaler_algo : str
			see get_scaled_f_scores

		Returns
		-------
		pd.DataFrame of scaled_f_score scores compared to background corpus
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

