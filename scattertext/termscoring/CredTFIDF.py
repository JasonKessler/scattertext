import math

import pandas as pd
from scipy.stats import norm

from scattertext.termscoring.CohensDCalculator import CohensDCalculator
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer
import numpy as np
from scipy.sparse import csr_matrix

import math

import pandas as pd
from scipy.stats import norm

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer
import numpy as np
from scipy.sparse import csr_matrix


class CredTFIDF(CorpusBasedTermScorer):
    '''
    Yoon Kim and Owen Zhang. Implementation of Credibility Adjusted Term Frequency: A Supervised Term Weighting
    Scheme for Sentiment Analysis and Text Classification. WASSA 2014.
    http://www.people.fas.harvard.edu/~yoonkim/data/cred-tfidf.pdf
    '''

    def get_score_df(self):
        '''
        :return: pd.DataFrame
        '''

        X = self._get_X().astype(np.float64)
        tf_i_d_pos, tf_i_d_neg = self._get_cat_and_ncat(X)
        return self._get_score_df_from_category_Xs(tf_i_d_neg, tf_i_d_pos)

    def _get_score_df_from_category_Xs(self, tf_i_d_neg, tf_i_d_pos):
        # Eq 2
        C_i_pos = tf_i_d_pos.sum(axis=0)  # number of times of a token occurs in pos class
        C_i_neg = tf_i_d_neg.sum(axis=0)  # number of times of a token occurs in neg class
        C_i = C_i_pos + C_i_neg  # total number of time a token occurs
        # s_i_pos = C_i_pos / C_i  # where s_i^(j) == 1
        # s_i_neg = C_i_neg / C_i  # where s_i^(j) == -1
        # Eq 4
        # "s_hatˆi is the average likelihood of making the correct classification
        # given token i's occurrence in the document, if i was the only token in
        # the document."
        s_hat_i = (np.power(C_i_pos, 2) + np.power(C_i_neg, 2)) / (np.power(C_i, 2))
        # Eq 5
        # Suppose sˆi = ˆsj = 0.75 for two different tokens
        # i and j, but Ci = 5 and Cj = 100. Intuition suggests that sˆj is a more credible score than
        # sˆi, and that sˆi should be shrunk towards the population
        # mean. Let sˆ be the (weighted) population mean.
        # That is,
        C = C_i.sum()

        s_hat = ((s_hat_i.A1 * C_i.A1) / C).sum()
        # Eq 6
        # We define credibility adjusted score for token i to
        # be, (Eqn 6) where γ is an additive smoothing parameter. If
        # Ci,k’s are small, then si ≈ sˆ (otherwise, si ≈ sˆi).
        # This is a form of Buhlmann credibility adjustment
        # from the actuarial literature (Buhlmann and Gisler,
        # 2005)
        s_bar_i = ((np.power(C_i_pos, 2) + np.power(C_i_neg, 2) + s_hat * self.eta)
                   / (np.power(C_i, 2) + self.eta))
        # Eq 7
        if self.use_sublinear:
            if not type(tf_i_d_pos) in [np.matrix, np.array]:
                tf_i_d_pos = tf_i_d_pos.todense()
                tf_i_d_neg = tf_i_d_neg.todense()
            adjpos_tf_idf = np.asarray(np.log(tf_i_d_pos + 0.5))
            adjneg_tf_idf = np.asarray(np.log(tf_i_d_neg + 0.5))
        else:
            # tf_bar_i_pos = tf_i_d_pos.multiply(0.5 + s_bar_i).todense()
            # tf_bar_i_neg = tf_i_d_neg.multiply(0.5 + s_bar_i).todense()
            adjpos_tf_idf = np.asarray(tf_i_d_pos.todense())
            adjneg_tf_idf = np.asarray(tf_i_d_neg.todense())
        s_bar_i_coef = (0.5 + s_bar_i).A1
        tf_bar_i_pos = adjpos_tf_idf
        tf_bar_i_neg = adjneg_tf_idf
        if self.use_cred:
            tf_bar_i_pos *= s_bar_i_coef
            tf_bar_i_neg *= s_bar_i_coef
        # Eq 8
        N = 1. * tf_i_d_pos.shape[0] + tf_bar_i_neg.shape[0]
        df_i = ((tf_i_d_pos > 0).astype(float).sum(axis=0)
                + (tf_i_d_neg > 0).astype(float).sum(axis=0))
        w_i_d_pos = tf_bar_i_pos * np.log(N / df_i).A1
        w_i_d_neg = tf_bar_i_neg * np.log(N / df_i).A1
        w_d_pos_l2 = 1.
        w_d_neg_l2 = 1.
        if self.use_l2_norm:
            w_d_pos_l2 = np.linalg.norm(w_i_d_pos, 2, axis=1)
            w_d_neg_l2 = np.linalg.norm(w_i_d_neg, 2, axis=1)
        pos_cred_tfidf = (w_i_d_pos.T
                          / w_d_pos_l2
                          ).mean(axis=1)
        neg_cred_tfidf = (w_i_d_neg.T
                          / w_d_neg_l2
                          ).mean(axis=1)
        score_df = pd.DataFrame({
            'pos_cred_tfidf': pos_cred_tfidf,
            'neg_cred_tfidf': neg_cred_tfidf,
            'delta_cred_tf_idf': pos_cred_tfidf - neg_cred_tfidf
        }, index=self._get_index())
        return score_df

    def _set_scorer_args(self, **kwargs):
        self.eta = kwargs.get('eta', 1.)
        self.use_sublinear = kwargs.get('use_sublinear', True)
        self.use_cred = kwargs.get('use_cred', True)
        self.use_l2_norm = kwargs.get('use_l2_norm', True)

    def get_scores(self, *args):
        return self.get_score_df()['delta_cred_tf_idf']

    def get_name(self):
        return "Delta mean %stf-idf" % ('cred-' if self.use_cred else '')

"""
class CredTFIDF(CorpusBasedTermScorer):
    '''
    !!! Not working

    Yoon Kim and Owen Zhang. Implementation of Credibility Adjusted Term Frequency: A Supervised Term Weighting
    Scheme for Sentiment Analysis and Text Classification. WASSA 2014.

    http://www.people.fas.harvard.edu/~yoonkim/data/cred-tfidf.pdf

    '''

    def get_score_df(self):
        '''
        :return: pd.DataFrame
        '''

        X = self._get_X().astype(np.float64)
        tf_i_d_pos, tf_i_d_neg = self._get_cat_and_ncat(X)
        return self._get_score_df_from_category_Xs(tf_i_d_neg, tf_i_d_pos)

    def _get_score_df_from_category_Xs(self, tf_i_d_neg, tf_i_d_pos):
        neg_cred_tfidf, pos_cred_tfidf = self.get_pos_neg_tfidf_matrices(tf_i_d_neg, tf_i_d_pos)
        print(pos_cred_tfidf.shape)
        print(neg_cred_tfidf.shape)
        score_df = CohensDCalculator().get_cohens_d_df(pos_cred_tfidf.T, neg_cred_tfidf.T)
        print('score_df', score_df.shape)
        print(score_df)
        print(pos_cred_tfidf.shape)
        print(neg_cred_tfidf.shape)

        score_df['pos_cred_tfidf'] = pos_cred_tfidf.mean(axis=1)
        score_df['neg_cred_tfidf'] = neg_cred_tfidf.mean(axis=1)
        score_df['delta_cred_tf_idf'] = score_df['pos_cred_tfidf'] - score_df['neg_cred_tfidf']

        return score_df

    def get_pos_neg_tfidf_matrices(self, tf_i_d_neg, tf_i_d_pos):
        # Eq 2
        C_i_pos = tf_i_d_pos.sum(axis=0)  # number of times of a token occurs in pos class
        C_i_neg = tf_i_d_neg.sum(axis=0)  # number of times of a token occurs in neg class
        C_i = C_i_pos + C_i_neg  # total number of time a token occurs
        # s_i_pos = C_i_pos / C_i  # where s_i^(j) == 1
        # s_i_neg = C_i_neg / C_i  # where s_i^(j) == -1
        # Eq 4
        # "s_hatˆi is the average likelihood of making the correct classification
        # given token i's occurrence in the document, if i was the only token in
        # the document."
        s_hat_i = (np.power(C_i_pos, 2) + np.power(C_i_neg, 2)) / (np.power(C_i, 2))
        # Eq 5
        # Suppose sˆi = ˆsj = 0.75 for two different tokens
        # i and j, but Ci = 5 and Cj = 100. Intuition suggests that sˆj is a more credible score than
        # sˆi, and that sˆi should be shrunk towards the population
        # mean. Let sˆ be the (weighted) population mean.
        # That is,
        C = C_i.sum()
        s_hat = ((s_hat_i.A1 * C_i.A1) / C).sum()
        # Eq 6
        # We define credibility adjusted score for token i to
        # be, (Eqn 6) where γ is an additive smoothing parameter. If
        # Ci,k’s are small, then si ≈ sˆ (otherwise, si ≈ sˆi).
        # This is a form of Buhlmann credibility adjustment
        # from the actuarial literature (Buhlmann and Gisler,
        # 2005)
        s_bar_i = ((np.power(C_i_pos, 2) + np.power(C_i_neg, 2) + s_hat * self.eta)
                   / (np.power(C_i, 2) + self.eta))
        # Eq 7
        if self.use_sublinear:
            if not type(tf_i_d_pos) in [np.matrix, np.array]:
                tf_i_d_pos = tf_i_d_pos.todense()
                tf_i_d_neg = tf_i_d_neg.todense()
            adjpos_tf_idf = np.asarray(np.log(tf_i_d_pos + 0.5))
            adjneg_tf_idf = np.asarray(np.log(tf_i_d_neg + 0.5))
        else:
            # tf_bar_i_pos = tf_i_d_pos.multiply(0.5 + s_bar_i).todense()
            # tf_bar_i_neg = tf_i_d_neg.multiply(0.5 + s_bar_i).todense()
            adjpos_tf_idf = np.asarray(tf_i_d_pos.todense())
            adjneg_tf_idf = np.asarray(tf_i_d_neg.todense())
        s_bar_i_coef = (0.5 + s_bar_i).A1
        tf_bar_i_pos = adjpos_tf_idf
        tf_bar_i_neg = adjneg_tf_idf
        if self.use_cred:
            tf_bar_i_pos *= s_bar_i_coef
            tf_bar_i_neg *= s_bar_i_coef
        # Eq 8
        N = 1. * tf_i_d_pos.shape[0] + tf_bar_i_neg.shape[0]
        df_i = ((tf_i_d_pos > 0).astype(float).sum(axis=0)
                + (tf_i_d_neg > 0).astype(float).sum(axis=0))
        w_i_d_pos = tf_bar_i_pos * np.log(N / df_i).A1
        w_i_d_neg = tf_bar_i_neg * np.log(N / df_i).A1
        w_d_pos_l2 = 1.
        w_d_neg_l2 = 1.
        if self.use_l2_norm:
            w_d_pos_l2 = np.linalg.norm(w_i_d_pos, 2, axis=1)
            w_d_neg_l2 = np.linalg.norm(w_i_d_neg, 2, axis=1)
        pos_X_cred_tfidf = w_i_d_pos.T / w_d_pos_l2
        neg_X_cred_tfidf = w_i_d_neg.T / w_d_neg_l2
        #pos_cred_tfidf = pos_X_cred_tfidf.mean(axis=1)
        #neg_cred_tfidf = neg_X_cred_tfidf.mean(axis=1)
        return pos_X_cred_tfidf, neg_X_cred_tfidf

    def _set_scorer_args(self, **kwargs):
        self.eta = kwargs.get('eta', 1.)
        self.use_sublinear = kwargs.get('use_sublinear', True)
        self.use_cred = kwargs.get('use_cred', True)
        self.use_l2_norm = kwargs.get('use_l2_norm', True)

    def get_scores(self, *args):
        return self.get_score_df()['delta_cred_tf_idf']

    def get_name(self):
        return "Delta mean %stf-idf" % ('cred-' if self.use_cred else '')
"""