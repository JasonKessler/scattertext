import pandas as pd
from scipy.stats import beta, norm

from scattertext.termranking.OncePerDocFrequencyRanker import OncePerDocFrequencyRanker
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class BetaPosterior(CorpusBasedTermScorer):
    '''
    Beta Posterior Scoring. Code adapted from
    https://github.com/serinachang5/gender-associations/blob/master/score_words.py (Chang 2019).

    Serina Chang and Kathleen McKeown. Automatically Inferring Gender Associations from Language. To appear
    in Empirical Methods in Natural Language Processing (EMNLP) 2019 (Short Paper).

    Method was originally introduced in
    David Bamman, Jacob Eisenstein, and Tyler Schnoebelen.  GENDER IDENTITY AND LEXICAL VARIATION IN SOCIAL MEDIA. 2014.

    Direct quote from Bamman (2014)

    Identifying gender markers. Our goal is to identify words that are used with
    unusual frequency by authors of a single gender. Assume that each term has an
    unknown likelihood fi, indicating the proportion of authors who use term i. For
    gender j, there are Nj authors, of whom kji use term i; the total count of the term i
    is ki. We ask whether the count kji is significantly larger than expected. Assuming
    a non-informative prior distribution on fi, the posterior distribution (conditioned on
    the observations ki and N) is Beta(ki, N-ki). The distribution of the gender-specific
    counts can be described by an integral over all possible fi. This integral defines the
    Beta-Binomial distribution (Gelman, Carlin, Stern, and Rubin 2004), and has a
    closed form solution. We mark a term as having a significant gender association if
    the cumulative distribution at the count kji is p < .05.

    ```
    >>> term_scorer = BetaPosterior(corpus).set_categories('Positive', ['Negative'], ['Plot']).get_score_df()

    ```
    '''

    def __init__(self, corpus, *args, **kwargs):
        CorpusBasedTermScorer.__init__(self, corpus, *args, **kwargs)
        self.set_term_ranker(OncePerDocFrequencyRanker)

    def _set_scorer_args(self, **kwargs):
        pass

    def get_scores(self, *args):
        return self.get_score_df()['score']

    def get_score_df(self):
        '''


        :return: pd.DataFrame
        '''
        term_freq_df = self.term_ranker_.get_ranks('')
        cat_freq_df = pd.DataFrame({
            'cat': term_freq_df[self.category_name],
            'ncat': term_freq_df[self.not_category_names].sum(axis=1),
        })
        if self.neutral_category_names:
            cat_freq_df['neut'] = term_freq_df[self.neutral_category_names].sum(axis=1)

        cat_freq_df['all'] = cat_freq_df.sum(axis=1)
        N = cat_freq_df['all'].sum()
        catN = cat_freq_df['cat'].sum()
        ncatN = cat_freq_df['ncat'].sum()

        cat_freq_df['cat_pct'] = cat_freq_df['cat'] * 1. / catN
        cat_freq_df['ncat_pct'] = cat_freq_df['ncat'] * 1. / ncatN

        def row_beta_posterior(row):
            return pd.Series({
                'cat_p': beta(row['all'], N - row['all']).sf(row['cat'] * 1. / catN),
                'ncat_p': beta(row['all'], N - row['all']).sf(row['ncat'] * 1. / ncatN),
            })

        p_val_df = cat_freq_df.apply(row_beta_posterior, axis=1)

        cat_freq_df['cat_p'] = p_val_df['cat_p']
        cat_freq_df['ncat_p'] = p_val_df['ncat_p']
        cat_freq_df['cat_z'] = norm.ppf(p_val_df['cat_p'])
        cat_freq_df['ncat_z'] = norm.ppf(p_val_df['ncat_p'])
        cat_freq_df['score'] = None
        cat_freq_df['score'][cat_freq_df['cat_pct'] == cat_freq_df['ncat_pct']] = 0
        cat_freq_df['score'][cat_freq_df['cat_pct'] < cat_freq_df['ncat_pct']] = cat_freq_df['ncat_z']
        cat_freq_df['score'][cat_freq_df['cat_pct'] > cat_freq_df['ncat_pct']] = -cat_freq_df['cat_z']
        return cat_freq_df

    def get_name(self):
        return "Beta Posterior"
