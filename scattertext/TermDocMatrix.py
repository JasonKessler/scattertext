import warnings
from copy import copy

import numpy as np
import pandas as pd
import scipy
from pandas.core.common import SettingWithCopyWarning
from scipy.sparse import csr_matrix
from scipy.stats import hmean, fisher_exact, rankdata, norm
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifierCV, LassoCV

from scattertext.CSRMatrixTools import delete_columns, CSRMatrixFactory
from scattertext.Common import DEFAULT_BETA, DEFAULT_SCALER_ALGO, DEFAULT_BACKGROUND_SCALER_ALGO, \
    DEFAULT_BACKGROUND_BETA
from scattertext.TermDocMatrixWithoutCategories import TermDocMatrixWithoutCategories
from scattertext.indexstore import IndexStore, IndexStoreFromList
from scattertext.termscoring.CornerScore import CornerScore

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

from scattertext.termscoring.ScaledFScore import InvalidScalerException, ScaledFScore


class CannotCreateATermDocMatrixWithASignleCategoryException(Exception):
    pass


class TermDocMatrix(TermDocMatrixWithoutCategories):
    '''
    !!! to do: refactor score functions into classes
    '''

    def __init__(self,
                 X,
                 mX,
                 y,
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
        if all(y == y[0]):
            raise CannotCreateATermDocMatrixWithASignleCategoryException(
                'Documents must be labeled with more than one category. All documents were labeled '
                'with category: "' + str(category_idx_store.getval(y[0])) + '"')
        TermDocMatrixWithoutCategories.__init__(self, X=X, mX=mX, term_idx_store=term_idx_store,
                                                metadata_idx_store=metadata_idx_store,
                                                unigram_frequency_path=unigram_frequency_path)
        self._y = y
        self._category_idx_store = category_idx_store

    def get_categories(self):
        '''
        Returns
        -------
        list
        Category names
        '''
        return self._category_idx_store.values()

    def old_get_term_freq_df(self):
        d = {'term': self._term_idx_store._i2val}
        for i, category in self._category_idx_store.items():
            d[category + ' freq'] = self._X[self._y == i].sum(axis=0).A1
        return pd.DataFrame(d).set_index('term')

    def get_term_freq_df(self, label_append=' freq'):
        '''
        Parameters
        -------
        label_append : str

        Returns
        -------
        pd.DataFrame indexed on terms, with columns giving frequencies for each
        '''

        '''
        row = self._row_category_ids()
        newX = csr_matrix((self._X.data, (row, self._X.indices)))
        return self._term_freq_df_from_matrix(newX)
        '''
        mat = self.get_term_freq_mat()
        return pd.DataFrame(mat,
                            index=pd.Series(self.get_terms(), name='term'),
                            columns=[str(c) + label_append for c in self.get_categories()])

    def get_term_freq_mat(self):
        '''
        Returns
        -------
        np.array with columns as categories and rows as terms
        '''
        freq_mat = np.zeros(shape=(self.get_num_terms(), self.get_num_categories()),
                            dtype=self.get_term_doc_mat().dtype)
        for cat_i in range(self.get_num_categories()):
            freq_mat[:, cat_i] = self._X[self._y == cat_i, :].sum(axis=0)
        return freq_mat

    def get_term_count_mat(self):
        '''
        Returns
        -------
        np.array with columns as categories and rows as terms
        '''
        freq_mat = np.zeros(shape=(self.get_num_terms(), self.get_num_categories()),
                            dtype=self.get_term_doc_mat().dtype)
        for cat_i in range(self.get_num_categories()):
            X = (self._X[self._y == cat_i, :] > 0).astype(int)
            freq_mat[:, cat_i] = X.sum(axis=0)
        return freq_mat

    def get_metadata_count_mat(self):
        '''
        Returns
        -------
        np.array with columns as categories and rows as terms
        '''
        freq_mat = np.zeros(shape=(self.get_num_metadata(), self.get_num_categories()),
                            dtype=self.get_metadata_doc_mat().dtype)
        for cat_i in range(self.get_num_categories()):
            mX = (self._mX[self._y == cat_i, :] > 0).astype(int)
            freq_mat[:, cat_i] = mX.sum(axis=0)
        return freq_mat

    def get_term_doc_count_df(self, label_append=' freq'):
        '''

        Returns
        -------
        pd.DataFrame indexed on terms, with columns the number of documents each term appeared in
        each category
        '''
        # row = self._row_category_ids()
        # newX = csr_matrix(((self._X.data > 0).astype(int), (row, self._X.indices)))
        # return self._ term_freq_df_from_matrix(newX)
        mat = self.get_term_count_mat()
        return pd.DataFrame(mat,
                            index=self.get_terms(),
                            columns=[str(c) + label_append for c in self.get_categories()])

    def get_metadata_doc_count_df(self, label_append=' freq'):
        '''

        Returns
        -------
        pd.DataFrame indexed on metadata, with columns the number of documents
        each metadata appeared in each category
        '''
        mat = self.get_metadata_count_mat()
        return pd.DataFrame(mat,
                            index=self.get_metadata(),
                            columns=[str(c) + label_append for c in self.get_categories()])

    def _term_freq_df_from_matrix(self, catX, label_append=' freq'):
        return self._get_freq_df_using_idx_store(catX, self._term_idx_store, label_append=label_append)

    def _get_freq_df_using_idx_store(self, catX, idx_store, label_append=' freq'):
        d = {'term': idx_store._i2val}
        for idx, cat in self._category_idx_store.items():
            try:
                d[str(cat) + label_append] = catX[idx, :].A[0]
            except IndexError:
                self._fix_problem_when_final_category_index_has_no_terms(cat, catX, d, label_append)
        return pd.DataFrame(d).set_index('term')

    def _fix_problem_when_final_category_index_has_no_terms(self, cat, catX, d, label_append=' freq'):
        d[str(cat) + label_append] = np.zeros(catX.shape[1])

    def get_metadata_freq_df(self, label_append=' freq'):
        '''
        Parameters
        -------
        label_append : str

        Returns
        -------
        pd.DataFrame indexed on metadata, with columns giving frequencies for each category
        '''
        '''
        row = self._row_category_ids_for_meta()
        newX = csr_matrix((self._mX.data, (row, self._mX.indices)))
        return self._metadata_freq_df_from_matrix(newX, label_append)
        '''
        freq_mat = np.zeros(shape=(self.get_num_metadata(), self.get_num_categories()),
                            dtype=self.get_metadata_doc_mat().dtype)
        for cat_i in range(self.get_num_categories()):
            freq_mat[:, cat_i] = self._mX[self._y == cat_i, :].sum(axis=0)
        return pd.DataFrame(freq_mat,
                            index=pd.Series(self.get_metadata(), name='term'),
                            columns=[str(c) + label_append for c in self.get_categories()])

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

    def _metadata_freq_df_from_matrix(self, catX, label_append=' freq'):
        return self._get_freq_df_using_idx_store(catX, self._metadata_idx_store, label_append)

    def get_category_names_by_row(self):
        '''
        Returns
        -------
        np.array of the category name for each row
        '''
        return np.array(self.get_categories())[self._y]

    def _change_document_type_in_matrix(self, X, new_doc_ids):
        new_data = self._make_all_positive_data_ones(X.data)
        newX = csr_matrix((new_data, (new_doc_ids, X.indices)))
        return newX

    def keep_only_these_categories(self, categories, ignore_absences=False):
        '''
        Non destructive category removal.

        Parameters
        ----------
        categories : list
            list of categories to keep
        ignore_absences : bool, False by default
            if categories does not appear, don't raise an error, just move on.

        Returns
        -------
        TermDocMatrix, new object with categories removed.
        '''
        if not ignore_absences:
            assert set(self.get_categories()) & set(categories) == set(categories)
        categories_to_remove = [c for c in self.get_categories() if c not in categories]
        return self.remove_categories(categories_to_remove)

    def remove_categories(self, categories, ignore_absences=False):
        '''
        Non destructive category removal.

        Parameters
        ----------
        categories : list
            list of categories to remove
        ignore_absences : bool, False by default
            if categories does not appear, don't raise an error, just move on.

        Returns
        -------
        TermDocMatrix, new object with categories removed.
        '''
        idx_to_delete_list = []
        existing_categories = set(self.get_categories())
        for category in categories:
            if category not in existing_categories:
                if not ignore_absences:
                    raise KeyError('Category %s not found' % (category))
                continue
            idx_to_delete_list.append(self._category_idx_store.getidx(category))
        new_category_idx_store = self._category_idx_store.batch_delete_idx(idx_to_delete_list)

        columns_to_delete = np.nonzero(np.isin(self._y, idx_to_delete_list))
        new_X = delete_columns(self._X.T, columns_to_delete).T
        new_mX = delete_columns(self._mX.T, columns_to_delete).T
        intermediate_y = self._y[~np.isin(self._y, idx_to_delete_list)]
        old_y_to_new_y = [self._category_idx_store.getidx(x)
                          for x in new_category_idx_store._i2val]
        new_y = np.array([old_y_to_new_y.index(i) if i in old_y_to_new_y else None
                          for i in range(intermediate_y.max() + 1)])[intermediate_y]

        new_metadata_idx_store = self._metadata_idx_store

        if self.metadata_in_use():
            meta_idx_to_delete = np.nonzero(new_mX.sum(axis=0).A1 == 0)[0]
            new_metadata_idx_store = self._metadata_idx_store.batch_delete_idx(meta_idx_to_delete)

        term_idx_to_delete = np.nonzero(new_X.sum(axis=0).A1 == 0)[0]
        new_term_idx_store = self._term_idx_store.batch_delete_idx(term_idx_to_delete)
        new_X = delete_columns(new_X, term_idx_to_delete)

        term_doc_mat_to_ret = self._make_new_term_doc_matrix(new_X, new_mX,
                                                             new_y.astype(int),
                                                             new_term_idx_store,
                                                             new_category_idx_store, new_metadata_idx_store,
                                                             ~np.isin(self._y, idx_to_delete_list))
        return term_doc_mat_to_ret

    def remove_terms_by_indices(self, idx_to_delete_list, non_text=False):
        '''
        Parameters
        ----------
        idx_to_delete_list, list
        non_text, bool

        Returns
        -------
        TermDocMatrix
        '''
        new_X, new_idx_store = self._get_X_after_delete_terms(idx_to_delete_list, non_text)
        return self._make_new_term_doc_matrix(
            new_X=self._X if non_text else new_X,
            new_mX=new_X if non_text else self._mX,
            new_y=self._y,
            new_term_idx_store=self._term_idx_store if non_text else new_idx_store,
            new_category_idx_store=self._category_idx_store,
            new_metadata_idx_store=new_idx_store if non_text else self._metadata_idx_store,
            new_y_mask=self._y == self._y
        )

    def change_category_names(self, new_category_names):
        if len(new_category_names) != self.get_num_categories():
            raise Exception("The number of category names passed (%s) needs to equal "
                            "the number of categories in the corpus (%s)." %
                            (len(new_category_names), self.get_num_categories()))
        return self._make_new_term_doc_matrix(
            new_category_idx_store=IndexStoreFromList.build(new_category_names)
        )

    def _make_new_term_doc_matrix(self,
                                  new_X=None,
                                  new_mX=None,
                                  new_y=None,
                                  new_term_idx_store=None,
                                  new_category_idx_store=None,
                                  new_metadata_idx_store=None,
                                  new_y_mask=None):
        return TermDocMatrix(X=new_X if new_X is not None else self._X,
                             mX=new_mX if new_mX is not None else self._mX,
                             y=new_y if new_y is not None else self._y,
                             term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
                             category_idx_store=new_category_idx_store if new_category_idx_store is not None else self._category_idx_store,
                             metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
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

    def get_corner_scores(self, category):
        ''' Computes corner score, which is inversely correlated
        to the Rudder score to the nearest upper-left or lower-right corner.
        Parameters
        ----------
        category : str
            category name to score

        Returns
        -------
            np.array
        '''
        return CornerScore.get_scores(
            *self._get_catetgory_and_non_category_word_counts(category)
        )

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
        try:
            from sklearn.cross_validation import cross_val_predict
        except:
            from sklearn.model_selection import cross_val_predict
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
        try:
            from sklearn.cross_validation import cross_val_predict
        except:
            from sklearn.model_selection import cross_val_predict
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
                            scaler_algo=DEFAULT_SCALER_ALGO,
                            beta=DEFAULT_BETA):
        ''' Computes scaled-fscores
        Parameters
        ----------
        category : str
            category name to score
        scaler_algo : str
          Function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'. Default.
        beta : float
            Beta in (1+B^2) * (Scale(P(w|c)) * Scale(P(c|w)))/(B^2*Scale(P(w|c)) + Scale(P(c|w))). Default.
        Returns
        -------
            np.array of harmonic means of scaled P(word|category) and scaled P(category|word)
        '''

        assert beta > 0
        cat_word_counts, not_cat_word_counts = self._get_catetgory_and_non_category_word_counts(category)
        scores = self._get_scaled_f_score_from_counts(cat_word_counts, not_cat_word_counts, scaler_algo, beta)
        return np.array(scores)

    def _get_scaled_f_score_from_counts(self, cat_word_counts, not_cat_word_counts, scaler_algo,
                                        beta=DEFAULT_BETA):
        '''
        scaler = self._get_scaler_function(scaler_algo)
        p_word_given_category = cat_word_counts.astype(np.float64) / cat_word_counts.sum()
        p_category_given_word = cat_word_counts.astype(np.float64) / (cat_word_counts + not_cat_word_counts)
        scores \
            = self._computer_harmoic_mean_of_probabilities_over_non_zero_in_category_count_terms(
            cat_word_counts, p_category_given_word, p_word_given_category, scaler
        )
        '''
        return ScaledFScore.get_scores(cat_word_counts, not_cat_word_counts, scaler_algo, beta=beta)

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
            scaler = lambda x: rankdata(x).astype(np.float64) / len(x)
        elif scaler_algo == 'normcdf':
            # scaler = lambda x: ECDF(x[cat_word_counts != 0])(x)
            scaler = lambda x: norm.cdf(x, x.mean(), x.std())
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
        df = self.get_term_and_background_counts()
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
        df = self.get_term_and_background_counts()
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
        df = self.get_term_and_background_counts()
        corpus_percentiles = self._get_percentiles_from_freqs(df['corpus'])
        background_percentiles = self._get_percentiles_from_freqs(df['background'])
        df['Rudder'] = (self._get_rudder_scores_for_percentile_pair(corpus_percentiles,
                                                                    background_percentiles))
        df = df.sort_values(by='Rudder', ascending=True)
        return df

    def _rescale_labels_to_neg_one_pos_one(self, category):
        return (self._get_mask_from_category(category)) * 2 - 1

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

    def get_term_category_frequencies(self, scatterchartdata):
        '''
        Applies the ranker in scatterchartdata to term-category frequencies.

        Parameters
        ----------
        scatterchartdata : ScatterChartData

        Returns
        -------
        pd.DataFrame
        '''
        term_ranker = scatterchartdata.term_ranker(self)
        if scatterchartdata.use_non_text_features:
            term_ranker.use_non_text_features()
        return term_ranker.get_ranks()

    def get_category_ids(self):
        '''
        Returns array of category ids

        Returns
        -------
        np.array
        '''
        return self._y

    def get_category_index_store(self):
        '''
        Returns IndexStore object mapping categories to ids

        Returns
        -------
        IndexStore
        '''
        return self._category_idx_store

    def recategorize(self, new_categories):
        '''
        Parameters
        ----------
        new_categories : array like
        String names of new categories. Length should be equal to number of documents

        Returns
        -------
        TermDocMatrix
        '''
        assert len(new_categories) == self.get_num_docs()

        new_category_idx_store = IndexStoreFromList.build(set(new_categories))
        new_y = np.array(new_category_idx_store.getidxstrictbatch(new_categories))

        new_tdm = self._make_new_term_doc_matrix(self._X, self._mX, new_y, self._term_idx_store, new_category_idx_store,
                                                 self._metadata_idx_store, new_y == new_y)
        return new_tdm

    def use_doc_labeled_terms_as_metadata(self, doc_labels, separator='_'):
        '''
        Makes the metadata of a new TermDocMatrix a copy of the term-document matrix, except each term is prefixed
        by its document's label followed by the separator.

        :param doc_labels: list[str], should be the same size as the number of documents in the TermDocMatrix.
        :param separator: str, default is '_'
        :return: self
        '''

        assert len(doc_labels) == self.get_num_docs()

        doc_labels = np.array(doc_labels)

        terms_in_corpus = np.array(self._term_idx_store.values())
        new_metadata_list = []
        new_meta_X = None

        ordered_doc_labels = list(sorted(set(doc_labels)))
        for doc_label in ordered_doc_labels:
            label_doc_mask = doc_labels == doc_label
            label_X = self._X[label_doc_mask, :]
            label_term_mask = (label_X.sum(axis=0) > 0).A1
            label_X = label_X[:, label_term_mask]
            cols_to_pad = len(new_metadata_list)

            new_metadata_list += [doc_label + separator + term
                                  for term in terms_in_corpus[label_term_mask]]
            if new_meta_X is None:
                new_meta_X = label_X
            else:
                label_X_pad = (CSRMatrixFactory()
                               .set_last_col_idx(cols_to_pad - 1)
                               .set_last_row_idx(sum(label_doc_mask) - 1)
                               .get_csr_matrix())
                padded_label_X = scipy.sparse.hstack([label_X_pad, label_X])
                new_meta_X.resize(new_meta_X.shape[0], padded_label_X.shape[1])
                new_meta_X = scipy.sparse.vstack([new_meta_X,
                                                  padded_label_X])

        new_metadata_idx_store = IndexStoreFromList.build(new_metadata_list)
        new_meta_X = new_meta_X.tocsr()
        new_mX = (CSRMatrixFactory()
                  .set_last_col_idx(new_meta_X.shape[1] - 1)
                  .set_last_row_idx(new_meta_X.shape[0] - 1)
                  .get_csr_matrix().tolil())
        start_row = 0
        for doc_label in ordered_doc_labels:
            label_doc_mask = doc_labels == doc_label
            num_rows = sum(label_doc_mask)
            new_mX[label_doc_mask, :] = new_meta_X[start_row:start_row + num_rows, :]
            start_row += num_rows

        new_mX = new_mX.tocsr()
        new_tdm = self._make_new_term_doc_matrix(self._X,
                                                 new_mX,
                                                 self._y,
                                                 self._term_idx_store,
                                                 self._category_idx_store,
                                                 new_metadata_idx_store,
                                                 self._y == self._y)
        return new_tdm

    def use_categories_as_metadata(self):
        '''
        Returns a TermDocMatrix which is identical to self except the metadata values are now identical to the
         categories present.

        :return: TermDocMatrix
        '''
        new_metadata_factory = CSRMatrixFactory()
        for i, category_idx in enumerate(self.get_category_ids()):
            new_metadata_factory[i, category_idx] = 1
        new_metadata = new_metadata_factory.get_csr_matrix()
        new_tdm = self._make_new_term_doc_matrix(self._X,
                                                 new_metadata,
                                                 self._y,
                                                 self._term_idx_store,
                                                 self._category_idx_store,
                                                 copy(self._category_idx_store),
                                                 self._y == self._y)
        return new_tdm

    def use_categories_as_metadata_and_replace_terms(self):
        '''
        Returns a TermDocMatrix which is identical to self except the metadata values are now identical to the
         categories present and term-doc-matrix is now the metadata matrix.

        :return: TermDocMatrix
        '''
        new_metadata_factory = CSRMatrixFactory()
        for i, category_idx in enumerate(self.get_category_ids()):
            new_metadata_factory[i, category_idx] = 1
        new_metadata = new_metadata_factory.get_csr_matrix()
        new_tdm = self._make_new_term_doc_matrix(self._mX,
                                                 new_metadata,
                                                 self._y,
                                                 self._metadata_idx_store,
                                                 self._category_idx_store,
                                                 copy(self._category_idx_store),
                                                 self._y == self._y)
        return new_tdm

    def get_num_categories(self):
        '''
        Returns the number of categories in the term document matrix
        :return: int
        '''
        return len(self.get_categories())
