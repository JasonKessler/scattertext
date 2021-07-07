import pandas as pd
import numpy as np
from scipy.stats import rankdata

from scattertext.termranking.AbsoluteFrequencyRanker import AbsoluteFrequencyRanker
from scattertext.termscoring.ScaledFScore import ScaledFScorePresetsNeg1To1


class TermCategoryRanker(object):
    def __init__(self,
                 scorer=ScaledFScorePresetsNeg1To1,
                 term_ranker=AbsoluteFrequencyRanker,
                 use_non_text_features=False):
        self.scorer = scorer
        self.term_ranker = term_ranker
        self.use_non_text_features = use_non_text_features

    def get_rank_df(self, term_doc_matrix):
        # tdf = term_doc_matrix.get_term_freq_df('')
        tdf, tdf_sum = self.__get_term_ranks_and_frequencies(term_doc_matrix)
        score_data = {}
        for category in term_doc_matrix.get_categories():
            focus = tdf[category].values
            background = tdf_sum.values - focus
            score_data[category] = self.scorer().get_scores(focus, background)
        return pd.DataFrame(score_data, index=tdf.index).apply(lambda x: rankdata(x, 'dense'))

    def __get_term_ranks_and_frequencies(self, term_doc_matrix):
        ranker = self.term_ranker(term_doc_matrix)
        if self.use_non_text_features:
            ranker = ranker.use_non_text_features()
        tdf = ranker.get_ranks('')
        tdf_sum = tdf.sum(axis=1)
        return tdf, tdf_sum

    def get_frequencies(self, term_doc_matrix):
        return self.__get_term_ranks_and_frequencies(term_doc_matrix)[1]

    def get_max_rank(self, term_doc_matrix):
        '''

        :param term_doc_matrix: TermDocMatrix
        :return: int
        '''
        rank_df = self.get_rank_df(term_doc_matrix)
        return rank_df.max().max()


class BaseAssociationCompactor(object):
    def __init__(self,
                 scorer=ScaledFScorePresetsNeg1To1,
                 term_ranker=AbsoluteFrequencyRanker,
                 use_non_text_features=False):
        self.scorer = TermCategoryRanker(scorer, term_ranker, use_non_text_features)

    def _prune_higher_ranked_terms(self, term_doc_matrix, rank_df, rank):
        terms_to_remove = rank_df.index[np.isnan(rank_df[rank_df <= rank])
            .apply(lambda x: all(x), axis=1)]
        return self._remove_terms(term_doc_matrix, terms_to_remove)

    def _remove_terms(self, term_doc_matrix, terms_to_remove):
        return term_doc_matrix.remove_terms(terms_to_remove, non_text=self.scorer.use_non_text_features)

class JSDCompactor(BaseAssociationCompactor):
    def __init__(self,
                 max_terms,
                 term_ranker=AbsoluteFrequencyRanker,
                 use_non_text_features=False):
        self.max_terms = max_terms
        BaseAssociationCompactor.__init__(self, term_ranker=term_ranker, use_non_text_features=use_non_text_features)

    def compact(self, term_doc_matrix, verbose=False):
        rank_df = self.scorer.get_rank_df(term_doc_matrix)
        p_df = rank_df/rank_df.sum(axis=0) + 0.001
        m = p_df.sum(axis=1)
        def lg(x): return np.log(x) / np.log(2)
        rank_df['Score'] = m * lg(1/m) - (p_df * lg(1/p_df)).sum(axis=1)
        terms_to_remove = rank_df.sort_values(
            by='Score', ascending=False
        ).iloc[self.max_terms:].index
        return term_doc_matrix.remove_terms(terms_to_remove, self.scorer.use_non_text_features)


class AssociationCompactor(BaseAssociationCompactor):
    def __init__(self,
                 max_terms,
                 scorer=ScaledFScorePresetsNeg1To1,
                 term_ranker=AbsoluteFrequencyRanker,
                 use_non_text_features=False,
                 include_n_most_frequent_terms=0):
        self.max_terms = max_terms
        self.include_n_most_frequent_terms = include_n_most_frequent_terms
        BaseAssociationCompactor.__init__(self, scorer, term_ranker, use_non_text_features)

    def compact(self, term_doc_matrix, verbose=False):
        '''
        Parameters
        ----------
        term_doc_matrix : TermDocMatrix
            Term document matrix object to compact
        Returns
        -------
        New term doc matrix
        '''
        rank_df = self.scorer.get_rank_df(term_doc_matrix)
        optimal_rank = self._find_optimal_rank(rank_df)

        terms_to_remove = rank_df.index[np.isnan(rank_df[rank_df <= optimal_rank])
            .apply(lambda x: all(x), axis=1)]

        if self.include_n_most_frequent_terms > 0:
            most_frequent_terms = self.scorer.get_frequencies(term_doc_matrix).sort_values(
                ascending=False
            ).index[:self.include_n_most_frequent_terms]
            terms_to_remove = set(terms_to_remove) - set(most_frequent_terms)

        compacted_term_doc_matrix = self._remove_terms(term_doc_matrix, terms_to_remove)

        if verbose:
            print('max terms', self.max_terms,
                  'optimal_rank', optimal_rank,
                  'num_terms', compacted_term_doc_matrix.get_num_terms())
        return compacted_term_doc_matrix

    def _get_num_terms_at_rank(self, rank_i, rank_df):
        return sum(np.isnan(rank_df[rank_df <= rank_i]).apply(lambda x: not all(x), axis=1))

    def _find_optimal_rank(self, ranks_df):
        max_rank = ranks_df.max().max()
        min_rank = 1
        last_max_rank = None
        last_min_rank = None
        while max_rank - 1 > min_rank:
            if last_max_rank is not None:
                if last_min_rank == min_rank and last_max_rank == max_rank:
                    raise Exception("Error. Potential infinite loop detected.")
            last_max_rank = max_rank
            last_min_rank = min_rank
            cur_rank = int((max_rank - min_rank) / 2) + min_rank
            num_terms = self._get_num_terms_at_rank(cur_rank, ranks_df)
            if num_terms > self.max_terms:
                max_rank = cur_rank
            elif num_terms < self.max_terms:
                min_rank = cur_rank
            else:
                return cur_rank
        return min_rank


class AssociationCompactorByRank(BaseAssociationCompactor):
    def __init__(self,
                 rank,
                 scorer=ScaledFScorePresetsNeg1To1,
                 term_ranker=AbsoluteFrequencyRanker,
                 use_non_text_features=False):
        self.rank = rank
        BaseAssociationCompactor.__init__(self, scorer, term_ranker, use_non_text_features)

    def compact(self, term_doc_matrix):
        '''
        Parameters
        ----------
        term_doc_matrix : TermDocMatrix
            Term document matrix object to compact
        Returns
        -------
        TermDocMatrix


        '''
        rank_df = self.scorer.get_rank_df(term_doc_matrix)
        return self._prune_higher_ranked_terms(term_doc_matrix, rank_df, self.rank)
