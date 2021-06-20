"""
Approach adapted from https://www.cis.upenn.edu/~ungar/sentiment/machine_learning_SA.pdf
"""
import logging

import numpy as np
import pandas as pd

from scattertext.continuous.coefficientbase import CoefficientBase


def ungar_transform(tdm):
    pw = tdm.sum(axis=0).A1 / tdm.sum()  # get prob(word)
    tdmd = tdm.todense()
    tdmdpw = tdmd.T
    #tdmdpw = np.multiply(tdmd, pw) # use word probabilities
    tdmdpwln = (tdmdpw / tdmdpw.sum(axis=1)).T # length normalized
    print(tdmdpwln.shape, tdm.shape)
    X = 2 * np.sqrt(tdmdpwln + 3. / 8)  # Anscombe transformed
    return X.T


class UngarCoefficients(CoefficientBase):
    def get_coefficient_df(self, corpus, document_scores):
        from statsmodels.regression.linear_model import OLS
        '''

        :param corpus: TermDocMatrix, should just have unigrams
        :param document_scores: np.array, continuous value for each document score
        :return: pd.DataFrame
        '''
        assert document_scores.shape == (corpus.get_num_docs(),)
        if any(' ' in t for t in self._get_terms(corpus)):
            logging.warning('UngerCoefficients is currently designed for only unigram terms. '
                            'Run corpus.get_unigram_corpus() before using this.')

        X = ungar_transform(self._get_tdm(corpus))
        model = OLS(document_scores, X.T).fit()
        df = pd.DataFrame({
            'Word': self._get_terms(corpus),
            'Beta': model.params,
            'Tstat': model.tvalues,
            'Frequency': corpus.get_term_doc_mat().sum(axis=0)[0].A1
        }).set_index('Word')

        return df

