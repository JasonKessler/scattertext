import numpy as np
import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class LogOddsRatio(CorpusBasedTermScorer):

    def _set_scorer_args(self, **kwargs):
        self.constant = kwargs.get('constant', 0.01)

    def get_scores(self, *args):
        '''
        In this case, args aren't used, since this information is taken
        directly from the corpus categories.

        Returns
        -------
        np.array, scores
        '''
        if self.tdf_ is None:
            raise Exception("Use set_categories('category name', ['not category name', ...]) " +
                            "to set the category of interest")

        y_i = self.tdf_['cat']
        y_j = self.tdf_['ncat']
        n_i, n_j = y_i.sum(), y_j.sum()
        delta_i_j = (np.log((y_i + self.constant) / (self.constant + n_i - y_i))
                     - np.log((y_j + self.constant) / (self.constant + n_j - y_j)))
        return delta_i_j

    def get_name(self):
        return 'Smoothed Log Odds Ratio'


LogOddsRatioScorer = LogOddsRatio


def log_odds_ratio_with_prior_from_counts(a: pd.Series, b: pd.Series) -> pd.Series:
    lor = (np.log(a / (np.sum(a) - a)) - np.log(b / (np.sum(b) - b)))
    lorstd = 1. / a + 1. / (np.sum(a) - a) + 1. / b + 1. / (np.sum(b) - b)
    log_odds_ratio_with_prior = lor / np.sqrt(lorstd)
    return log_odds_ratio_with_prior


class LogOddsRatioUninformativePriorScorer(CorpusBasedTermScorer):
    def get_name(self) -> str:
        return 'Log Odds Ratio w/ Uninformative Prior'

    def _set_scorer_args(self, **kwargs):
        self.alpha = kwargs.get('alpha', 0.01)

    def get_scores(self, *args) -> pd.Series:
        rank_df = self.term_ranker_.get_ranks('')
        a = rank_df[self.category_name] + self.alpha
        b = rank_df[self.not_category_names].sum(axis=1) + self.alpha
        return log_odds_ratio_with_prior_from_counts(a, b)



class LogOddsRatioInformativePriorScorer(CorpusBasedTermScorer):
    """
    priors = (st.PriorFactory(unigram_corpus,
                          category='Positive',
                          not_categories=['Negative'],
                          starting_count=0.01)
          .use_neutral_categories()
              .get_priors())
    html = st.produce_frequency_explorer(
        unigram_corpus,
        category='Positive',
        category_name='Negative',
        not_category_name='Negative',
        term_scorer=st.LogOddsRatioInformativePriorScorer,
        term_scorer_kwargs={'prior_scale': 6},
        metadata=get_heading,
        minimum_term_frequency=0,
        grey_threshold=0,
    )
    """

    def _set_scorer_args(self, prior_counts, prior_scale):
        self.prior_counts = prior_counts
        self.prior_scale = prior_scale

    def get_scores(self):
        rank_df = self.term_ranker_.get_ranks('')
        a = rank_df[self.category_name] + self.prior_counts
        b = rank_df[self.not_category_names].sum(axis=1) + self.prior_counts

        ap = a + self.prior_counts * self.prior_scale * sum(a) / sum(self.prior_counts.values)
        bp = b + self.prior_counts * self.prior_scale * sum(b) / sum(self.prior_counts.values)
        return log_odds_ratio_with_prior_from_counts(ap, bp)

    def get_name(self):
        return 'Log Odds Ratio w/ Informative Prior'
