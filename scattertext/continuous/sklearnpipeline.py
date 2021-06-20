import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import RidgeCV, ElasticNetCV, LassoCV
from sklearn.pipeline import Pipeline

from scattertext.continuous.coefficientbase import CoefficientBase


class RidgeCoefficients(CoefficientBase):
    def get_coefficient_df(self, corpus, document_scores, pipeline=None):
        '''

        :param corpus: TermDocMatrix, should just have unigrams
        :param document_scores: np.array, continuous value for each document score
        :return: pd.DataFrame
        '''
        assert document_scores.shape == (corpus.get_num_docs(),)
        tdm = self._get_tdm(corpus)

        model = self._get_default_pipeline(pipeline)
        model.fit(X=tdm.toarray(), y=document_scores)

        df = pd.DataFrame({
            'Word': self._get_terms(corpus),
            'Beta': model.named_steps['lr'].coef_,
            'Frequency': self._get_tdm(corpus).sum(axis=0)[0].A1
        }).set_index('Word')

        return df

    def _get_default_pipeline(self, pipeline):
        return Pipeline([
            ('tfidf', TfidfTransformer(sublinear_tf=True)),
            ('lr', (RidgeCV()))
        ]) if pipeline is None else pipeline
