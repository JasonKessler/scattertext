import pandas as pd
import numpy as np


class CategoryProjection(object):
    def __init__(self, category_corpus, category_counts, projection):
        self.category_corpus = category_corpus
        self.category_counts = category_counts
        self.projection = projection

    def get_pandas_projection(self, x_dim=0, y_dim=1):
        '''

        :param x_dim: int
        :param y_dim: int
        :return: pd.DataFrame
        '''
        return pd.DataFrame({'term': self.category_corpus.get_metadata(),
                             'x': self.projection.T[x_dim],
                             'y': self.projection.T[y_dim]}).set_index('term')

    def get_axes_labels(self, num_terms=5, x_dim=0, y_dim=1):
        dim_term = np.matrix(self.category_counts.values) * self.projection[:, [x_dim, y_dim]]
        df = pd.DataFrame(dim_term, index=self.category_corpus.get_terms(), columns=['x', 'y'])
        return {'x_pos': list(df.sort_values(by='x', ascending=False).index[:num_terms]),
                'x_neg': list(df.sort_values(by='x', ascending=True).index[:num_terms]),
                'y_pos': list(df.sort_values(by='y', ascending=False).index[:num_terms]),
                'y_neg': list(df.sort_values(by='y', ascending=True).index[:num_terms])}
