import pandas as pd
import numpy as np
from scipy.stats import rankdata

from scattertext.termscoring.ScaledFScore import ScaledFScorePresetsNeg1To1


class AssociationCompactor(object):
    def __init__(self, max_terms, scorer=ScaledFScorePresetsNeg1To1):
        self.max_terms = max_terms
        self.scorer = scorer

    def compact(self, term_doc_matrix):
        '''
        Parameters
        ----------
        term_doc_matrix : TermDocMatrix
            Term document matrix object to compact

        Returns
        -------
        New term doc matrix
        '''
        rank_df = self._get_rank_df(term_doc_matrix)
        optimal_rank = self._find_optimal_rank(rank_df)
        term_to_remove = rank_df.index[np.isnan(rank_df[rank_df <= optimal_rank])
            .apply(lambda x: all(x), axis=1)]
        return term_doc_matrix.remove_terms(term_to_remove)

    def _get_rank_df(self, corpus):
        tdf = corpus.get_term_freq_df('')
        tdf_sum = tdf.sum(axis=1)
        score_data = {}
        for category in corpus.get_categories():
            score_data[category] = self.scorer().get_scores(tdf[category], tdf_sum - tdf[category])
        return pd.DataFrame(score_data, index=tdf.index).apply(lambda x: rankdata(x, 'dense'))

    def _get_num_terms(self, rank_i, rank_df):
        return sum(np.isnan(rank_df[rank_df <= rank_i]).apply(lambda x: not all(x), axis=1))

    def _find_optimal_rank(self, ranks_df):
        max_rank = ranks_df.max().max()
        min_rank = 1

        while max_rank - 1 > min_rank:
            cur_rank = int((max_rank - min_rank) / 2) + min_rank
            num_terms = self._get_num_terms(cur_rank, ranks_df)
            if num_terms > self.max_terms:
                max_rank = cur_rank
            elif num_terms < self.max_terms:
                min_rank = cur_rank
            else:
                return cur_rank
        return min_rank
