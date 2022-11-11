import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau

from scattertext.continuous.coefficientbase import CoefficientBase

class Correlations(CoefficientBase):
    def __init__(self, use_non_text=False):
        self.set_correlation_type('pearsonr')
        CoefficientBase.__init__(self, use_non_text=use_non_text)

    def set_correlation_type(self, correlation_type: str = 'pearsonr') -> 'Correlations':
        assert correlation_type in ['pearsonr', 'spearmanr', 'kendalltau']
        self.correlation_type_ = correlation_type
        if correlation_type == 'pearsonr':
            self.cols_ = ['r', 'p']
        if correlation_type == 'spearmanr':
            self.cols_ = ['r', 'p']
        if correlation_type == 'kendalltau':
            self.cols_ = ['tau', 'p']
        return self

    def __get_correlation_funct(self):
        if self.correlation_type_ == 'pearsonr':
            return pearsonr
        if self.correlation_type_ == 'spearmanr':
            return spearmanr
        if self.correlation_type_ == 'kendalltau':
            return kendalltau


    def get_correlation_df(self, corpus, document_scores):
        '''

        :param corpus: TermDocMatrix, should just have unigrams
        :param document_scores: np.array, continuous value for each document score
        :return: pd.DataFrame
        '''
        assert document_scores.shape == (corpus.get_num_docs(),)
        tdm = self._get_tdm(corpus)

        return pd.DataFrame(
            [self.__get_correlation_funct()(tdm.T[i].todense().A1, document_scores) for i in range(tdm.shape[1])],
            columns=self.cols_
        ).assign(
            Term=self._get_terms(corpus),
            Frequency=(tdm > 0).sum(axis=0).A1
        ).set_index('Term').reindex(self._get_terms(corpus))

