import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata

from scattertext.Common import DEFAULT_SCALER_ALGO, DEFAULT_BETA


class InvalidScalerException(Exception):
    pass


class ScoreBalancer(object):
    @staticmethod
    def balance_scores(cat_scores, not_cat_scores):
        scores = ScoreBalancer.balance_scores_and_dont_scale(cat_scores, not_cat_scores)
        return ScoreBalancer._zero_centered_scale(scores)

    @staticmethod
    def balance_scores_and_dont_scale(cat_scores, not_cat_scores):
        '''
        median = np.median(cat_scores)
        scores = np.zeros(len(cat_scores)).astype(np.float)
        scores[cat_scores > median] = cat_scores[cat_scores > median]
        not_cat_mask = cat_scores < median if median != 0 else cat_scores <= median
        scores[not_cat_mask] = -not_cat_scores[not_cat_mask]
        '''
        scores = np.zeros(len(cat_scores)).astype(np.float)
        scores[cat_scores > not_cat_scores] = cat_scores[cat_scores > not_cat_scores]
        scores[cat_scores < not_cat_scores] = -not_cat_scores[cat_scores < not_cat_scores]
        return scores

    @staticmethod
    def _zero_centered_scale(ar):
        ar[ar > 0] = ScoreBalancer._scale(ar[ar > 0])
        ar[ar < 0] = -ScoreBalancer._scale(-ar[ar < 0])
        return (ar + 1) / 2.

    @staticmethod
    def _scale(ar):
        if len(ar) == 0:
            return ar
        if ar.min() == ar.max():
            return np.full(len(ar), 0.5)
        return (ar - ar.min()) / (ar.max() - ar.min())


class ScaledFScorePresets(object):
    def __init__(self,
                 scaler_algo=DEFAULT_SCALER_ALGO,
                 beta=DEFAULT_BETA,
                 one_to_neg_one=False,
                 priors=None,
                 use_score_difference=False,
                 ):
        self.scaler_algo_ = scaler_algo
        self.beta_ = beta
        self.one_to_neg_one_ = one_to_neg_one
        self.priors_ = priors
        self.use_score_difference_ = use_score_difference
        assert self.beta_ > 0

    def get_name(self):
        return 'Scaled F-Score'

    def get_default_score(self):
        if self.one_to_neg_one_:
            return 0
        return 0.5

    def get_scores(self, cat_word_counts, not_cat_word_counts):
        '''
        Parameters
        ----------
        cat_word_counts : np.array
            category counts
        not_cat_word_counts : np.array
            not category counts

        Returns
        -------
        np.array
            scores
        '''
        cat_scores = self.get_scores_for_category(cat_word_counts,
                                                  not_cat_word_counts)
        not_cat_scores = self.get_scores_for_category(not_cat_word_counts,
                                                      cat_word_counts)
        if self.use_score_difference_:
            scores = ((cat_scores - not_cat_scores) + 1.) / 2.
        else:
            scores = ScoreBalancer.balance_scores(cat_scores, not_cat_scores)
        if self.one_to_neg_one_:
            return 2 * scores - 1
        else:
            return scores

    def get_scores_for_category(self, cat_word_counts, not_cat_word_counts):
        '''
        Parameters
        ----------
        cat_word_counts : np.array
            category counts
        not_cat_word_counts : np.array
            not category counts

        Returns
        -------
        np.array
            scores
        '''
        beta = self.beta_
        # import pdb; pdb.set_trace()
        assert len(cat_word_counts) == len(not_cat_word_counts)
        old_cat_word_counts = None
        if type(cat_word_counts) == pd.Series:
            assert all(cat_word_counts.index == not_cat_word_counts.index)

            old_cat_word_counts = cat_word_counts
            cat_word_counts = cat_word_counts.values
        if type(not_cat_word_counts) == pd.Series:
            not_cat_word_counts = not_cat_word_counts.values
        if self.priors_ is not None:
            p = self.priors_
            assert len(p) == len(cat_word_counts)
            precision = ((cat_word_counts + p * 1.) /
                         (cat_word_counts + not_cat_word_counts + 2 * p))
            recall = (cat_word_counts + p) * 1. / (cat_word_counts.sum() + p.sum())
        else:
            precision = (cat_word_counts * 1. / (cat_word_counts + not_cat_word_counts))
            recall = cat_word_counts * 1. / cat_word_counts.sum()
        precision_normcdf = ScaledFScore._safe_scaler(self.scaler_algo_, precision)
        recall_normcdf = ScaledFScore._safe_scaler(self.scaler_algo_, recall)
        scores = self._weighted_h_mean(precision_normcdf, recall_normcdf)
        scores[np.isnan(scores)] = 0.
        if old_cat_word_counts is not None:
            return pd.Series(scores, index=old_cat_word_counts.index)
        return scores

    def _weighted_h_mean(self, precision_normcdf, recall_normcdf):
        scores = (1 + self.beta_ ** 2) * (precision_normcdf * recall_normcdf) \
                 / ((self.beta_ ** 2) * precision_normcdf + recall_normcdf)
        return scores


class ScaledFScorePresetsNeg1To1(ScaledFScorePresets):
    @staticmethod
    def get_default_score():
        return 0

    def get_scores(self, cat_word_counts, not_cat_word_counts):
        scores = ScaledFScorePresets.get_scores(self, cat_word_counts, not_cat_word_counts)
        return scores * 2 - 1


class ScaledFZScore(ScaledFScorePresets):
    @staticmethod
    def get_default_score():
        return 0

    def get_scores(self, cat_word_counts, not_cat_word_counts):
        sfs = ScaledFScorePresets.get_scores(self, cat_word_counts, not_cat_word_counts)
        # sfs = self.get_score_deltas(cat_word_counts, not_cat_word_counts)
        # import pdb; pdb.set_trace()
        # return (sfs - 0.5) / np.std(sfs - 0.5)
        return (sfs - sfs.mean()) / np.std(sfs)

    def get_name(self):
        return "Scaled F-Score Z-Score"

    def get_score_deltas(self, cat_word_counts, not_cat_word_counts):
        cat_scores = ScaledFScorePresets.get_scores_for_category(
            self, cat_word_counts, not_cat_word_counts)
        not_cat_scores = ScaledFScorePresets.get_scores_for_category(
            self, not_cat_word_counts, cat_word_counts)
        return np.log(cat_scores) - np.log(not_cat_scores)

    def get_p_vals(self, X):
        '''
        Parameters
        ----------
        X : np.array
            Array of word counts, shape (N, 2) where N is the vocab size.  X[:,0] is the
            positive class, while X[:,1] is the negative class. None by default

        Returns
        -------
        np.array of p-values

        '''
        z_scores = self.get_scores(X[:, 0], X[:, 1])
        return norm.cdf(z_scores)


class ScaledFZScorePrior(ScaledFZScore):
    def __init__(self, prior, alpha=1, scaler_algo=DEFAULT_SCALER_ALGO, beta=DEFAULT_BETA):
        self.prior = prior
        self.alpha = alpha
        ScaledFZScore.__init__(self, scaler_algo, beta)

    def get_name(self):
        return 'SFS w/ Informative Prior Z-Score'

    def apply_prior(self, c):
        n = np.sum(c)
        prior_scale = (np.sum(c) * self.alpha * 1. / np.sum(self.prior))
        return c + (self.prior * prior_scale)

    def get_scores(self, cat_word_counts, not_cat_word_counts):
        sfs = ScaledFScorePresets.get_scores(self, self.apply_prior(cat_word_counts),
                                             self.apply_prior(not_cat_word_counts))
        # sfs = self.get_score_deltas(cat_word_counts, not_cat_word_counts)
        # import pdb; pdb.set_trace()
        # return (sfs - 0.5) / np.std(sfs - 0.5)
        return (sfs - sfs.mean()) / np.std(sfs)

    def get_name(self):
        return "SFS Z-Scores"

    def get_score_deltas(self, cat_word_counts, not_cat_word_counts):
        cat_scores = ScaledFScorePresets.get_scores_for_category(
            self,
            self.apply_prior(cat_word_counts),
            self.apply_prior(not_cat_word_counts))
        not_cat_scores = ScaledFScorePresets.get_scores_for_category(
            self,
            self.apply_prior(not_cat_word_counts),
            self.apply_prior(cat_word_counts))
        return np.log(cat_scores) - np.log(not_cat_scores)


class ScaledFScore(object):
    @staticmethod
    def get_default_score():
        return 0.5

    @staticmethod
    def get_scores(cat_word_counts, not_cat_word_counts,
                   scaler_algo=DEFAULT_SCALER_ALGO, beta=DEFAULT_BETA):
        ''' Computes balanced scaled f-scores
        Parameters
        ----------
        cat_word_counts : np.array
            category counts
        not_cat_word_counts : np.array
            not category counts
        scaler_algo : str
            Function that scales an array to a range \in [0 and 1]. Use 'percentile', 'normcdf'. Default.
        beta : float
            Beta in (1+B^2) * (Scale(P(w|c)) * Scale(P(c|w)))/(B^2*Scale(P(w|c)) + Scale(P(c|w))). Default.
        Returns
        -------
            np.array
            Harmonic means of scaled P(word|category)
             and scaled P(category|word) for >median half of scores.  Low scores are harmonic means
             of scaled P(word|~category) and scaled P(~category|word).  Array is squashed to between
             0 and 1, with 0.5 indicating a median score.
        '''

        cat_scores = ScaledFScore.get_scores_for_category(cat_word_counts,
                                                          not_cat_word_counts,
                                                          scaler_algo,
                                                          beta)
        not_cat_scores = ScaledFScore.get_scores_for_category(not_cat_word_counts,
                                                              cat_word_counts,
                                                              scaler_algo, beta)
        return ScoreBalancer.balance_scores(cat_scores, not_cat_scores)

    @staticmethod
    def get_scores_for_category(cat_word_counts,
                                not_cat_word_counts,
                                scaler_algo=DEFAULT_SCALER_ALGO,
                                beta=DEFAULT_BETA):
        ''' Computes unbalanced scaled-fscores
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
            np.array of harmonic means of scaled P(word|category) and scaled P(category|word).
        '''
        assert beta > 0
        old_cat_word_counts = None
        if type(cat_word_counts) == pd.Series:
            old_cat_word_counts = cat_word_counts
            cat_word_counts = cat_word_counts.values

        if type(not_cat_word_counts) == pd.Series:
            not_cat_word_counts = not_cat_word_counts.values

        precision = (cat_word_counts * 1. / (cat_word_counts + not_cat_word_counts))
        recall = cat_word_counts * 1. / cat_word_counts.sum()
        precision_normcdf = ScaledFScore._safe_scaler(scaler_algo, precision)
        recall_normcdf = ScaledFScore._safe_scaler(scaler_algo, recall)
        scores_numerator = (1 + beta ** 2) * (precision_normcdf * recall_normcdf)
        scores_denominator = ((beta ** 2) * precision_normcdf + recall_normcdf)
        scores_denominator[scores_denominator == 0]  = 1
        scores = scores_numerator/scores_denominator
        scores[np.isnan(scores)] = 0.
        if old_cat_word_counts is None:
            return scores
        else:
            return pd.Series(scores, index=old_cat_word_counts.index)

    @staticmethod
    def _get_scaled_f_score_from_counts(cat_word_counts, not_cat_word_counts, scaler_algo, beta=DEFAULT_BETA):
        p_word_given_category = cat_word_counts.astype(np.float) / cat_word_counts.sum()
        p_category_given_word = cat_word_counts * 1. / (cat_word_counts + not_cat_word_counts)
        scores \
            = ScaledFScore._get_harmonic_mean_of_probabilities_over_non_zero_in_category_count_terms \
            (cat_word_counts, p_category_given_word, p_word_given_category, scaler_algo, beta)
        return scores

    @staticmethod
    def _safe_scaler(algo, ar):
        if algo == 'none':
            return ar
        scaled_ar = ScaledFScore._get_scaler_function(algo)(ar)
        if np.isnan(scaled_ar).any():
            return ScaledFScore._get_scaler_function('percentile')(scaled_ar)
        return scaled_ar

    @staticmethod
    def _get_scaler_function(scaler_algo):
        scaler = None
        if scaler_algo == 'normcdf':
            scaler = lambda x: norm.cdf(x, x.mean(), x.std())
        elif scaler_algo == 'lognormcdf':
            scaler = lambda x: norm.cdf(np.log(x), np.log(x).mean(), np.log(x).std())
        elif scaler_algo == 'percentile':
            scaler = lambda x: rankdata(x).astype(np.float64) / len(x)
        elif scaler_algo == 'percentiledense':
            scaler = lambda x: rankdata(x, method='dense').astype(np.float64) / len(x)
        elif scaler_algo == 'ecdf':
            from statsmodels.distributions import ECDF
            scaler = lambda x: ECDF(x)
        elif scaler_algo == 'none':
            scaler = lambda x: x
        else:
            raise InvalidScalerException("Invalid scaler alogrithm.  Must be either percentile or normcdf.")
        return scaler
