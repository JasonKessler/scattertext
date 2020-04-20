import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from scattertext.diachronic.BubbleDiachronicVisualization import BubbleDiachronicVisualization
from scattertext.diachronic.DiachronicVisualizer import DiachronicVisualizer


class DiachronicTermMiner(object):
    def __init__(self,
                 corpus,
                 num_terms=40,
                 start_category=None,
                 timesteps_to_lag=5,
                 seasonality_column=None):
        self.corpus_ = corpus
        self.num_terms_ = num_terms
        self.sorted_categores_ = np.array(sorted(corpus.get_categories()))
        if timesteps_to_lag > len(self.sorted_categores_):
            raise Exception("Too many timesteps to lag. There are only %s categories" %
                            len(self.sorted_categores_))
        self.timesteps_to_lag_ = timesteps_to_lag
        if start_category is None:
            self.start_category_ = sorted(corpus.get_categories())[timesteps_to_lag]
        else:
            if start_category not in corpus.get_categories():
                raise Exception("start_category %s needs to be a category in corpus" % (start_category))
            if start_category in self.sorted_categores_[:timesteps_to_lag]:
                raise Exception("start_category %s should have at least %s categories before it"
                                % (start_category, timesteps_to_lag))
            self.start_category_ = start_category
        if seasonality_column:
            if seasonality_column not in self.corpus_.get_df().columns:
                raise Exception("seasonality_column should be none or a column in the source dataframe")
        self.seasonality_column_ = seasonality_column

    def get_display_dataframe(self):
        '''
        Gets list of terms to display that have some interesting diachronic variation.

        Returns
        -------
        pd.DataFrame

        e.g.,
                   term variable  frequency  trending
        2            in   200310        1.0  0.000000
        19          for   200310        1.0  0.000000
        20           to   200311        1.0  0.000000
        '''
        X = self.corpus_.get_term_doc_mat()
        categories = pd.Series(self.corpus_.get_category_ids())
        cat_ar = np.array(self.corpus_.get_categories())
        cat_idx_sort = np.argsort(cat_ar)
        if self.seasonality_column_:
            seasonality_ar = np.array(self.corpus_.get_df()[self.seasonality_column_])

        terms = self.corpus_.get_terms()
        category_idx_store = self.corpus_.get_category_index_store()

        data = {}
        seasondata = {}
        for i, cati in enumerate(cat_idx_sort):
            cat = cat_ar[cati]
            if cat >= self.start_category_ and i > self.timesteps_to_lag_:
                neg_cats = self.sorted_categores_[i - self.timesteps_to_lag_:i]
                neg_mask = categories.isin(category_idx_store.getidxstrictbatch(neg_cats)).values
                scores = self._regress_terms(X, cat, categories, category_idx_store, neg_mask, terms)
                data[cat] = scores
                if self.seasonality_column_:
                    neg_cats = set(
                        categories[(seasonality_ar == seasonality_ar[cati]) & (categories != categories[cati])])
                    neg_mask = categories.isin(neg_cats).values
                    scores = self._regress_terms(X, cat, categories, category_idx_store, neg_mask, terms)
                    seasondata[cat] = scores
        coefs = pd.DataFrame(data)
        pos_coefs = (coefs.apply(lambda x: (x > 0) * x, axis=1)
                     .sum(axis=1)
                     .sort_values(ascending=False))

        term_cat_counts = self.corpus_.get_term_freq_df('')[coefs.columns]

        def dense_percentile(x):
            # ranks = rankdata(x, 'dense')
            return pd.Series(x / x.max(), index=x.index)

        rank_df = pd.DataFrame({'coefr': dense_percentile(pos_coefs),
                                'freqr': dense_percentile(term_cat_counts.max(axis=1)),
                                'coef': pos_coefs,
                                'freq': term_cat_counts.max(axis=1)})
        if self.seasonality_column_:
            seasoncoefs = (pd.DataFrame(seasondata).sum(axis=1))
            rank_df['seasoncoefr'] = dense_percentile(
                seasoncoefs.sort_values(ascending=False) + np.abs(seasoncoefs.min()))
            weights = [2, 1, 1]
            vals = ['freqr', 'coefr', 'seasoncoefr']

            def gethmean(x):
                if min(x[vals]) == 0:
                    return 0
                return sum(weights) * 1. / sum([weights[i] / x[val] for i, val in enumerate(vals)])

            rank_df['hmean'] = rank_df.apply(gethmean, axis=1)
        else:
            beta = 0.5
            rank_df['hmean'] = (rank_df
                                .apply(lambda x: 0 if min(x) == 0 else
            (1 + beta ** 2) * (x.coefr * x.freqr) / ((beta ** 2 * x.coefr) + x.freqr),
                                       axis=1))
        rank_df = rank_df.sort_values(by='hmean', ascending=False)
        display_df = pd.merge(
            (term_cat_counts
             .loc[rank_df.iloc[:self.num_terms_].index]
             .reset_index()
             .melt(id_vars=['index'])
             .rename(columns={'index': 'term', 'value': 'frequency'})),
            (coefs.loc[rank_df.iloc[:self.num_terms_].index]
             .reset_index()
             .melt(id_vars=['index'])
             .rename(columns={'index': 'term', 'value': 'trending'})),
            on=['term', 'variable']
		)
        display_df[display_df['frequency'] == 0] = np.nan
        display_df = display_df.dropna()
        return display_df[display_df.term.isin(rank_df.index)]

    def visualize(self, visualizer=BubbleDiachronicVisualization):
        assert issubclass(visualizer, DiachronicVisualizer)
        return visualizer.visualize(self.get_display_dataframe())

    def _regress_terms(self, X, cat, categories, category_idx_store, neg_mask, terms):
        pos_mask = categories.isin(category_idx_store.getidxstrictbatch([cat])).values
        catX = X[neg_mask | pos_mask, :]
        catY = np.zeros(catX.shape[0]).astype(bool)
        catY[pos_mask[neg_mask | pos_mask]] = True
        scores = (pd.Series(LogisticRegression(penalty='l2').fit(catX, catY).coef_[0], index=terms)
                  .sort_values(ascending=False))
        return scores
