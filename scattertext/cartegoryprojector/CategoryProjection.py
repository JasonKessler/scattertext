import pandas as pd
import numpy as np

from scattertext.Scalers import stretch_neg1_to_1


class CategoryProjection(object):
    def __init__(self, category_corpus, category_counts, projection, x_dim=0, y_dim=1):
        self.category_corpus = category_corpus
        self.category_counts = category_counts
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.projection = projection

    def get_pandas_projection(self):
        '''

        :param x_dim: int
        :param y_dim: int
        :return: pd.DataFrame
        '''
        return pd.DataFrame({'term': self.category_corpus.get_metadata(),
                             'x': self.projection.T[self.x_dim],
                             'y': self.projection.T[self.y_dim]}).set_index('term')

    def get_axes_labels(self, num_terms=5):
        df = self.get_term_projection()
        return {'right': list(df.sort_values(by='x', ascending=False).index[:num_terms]),
                'left': list(df.sort_values(by='x', ascending=True).index[:num_terms]),
                'top': list(df.sort_values(by='y', ascending=False).index[:num_terms]),
                'bottom': list(df.sort_values(by='y', ascending=True).index[:num_terms])}

    def get_nearest_terms(self, num_terms=5):
        df = self.get_term_projection().apply(stretch_neg1_to_1)
        return {
            'top_right': ((df.x - 1) ** 2 + (df.y - 1) ** 2).sort_values().index[:num_terms].values,
            'top': (df.x ** 2 + (df.y - 1) ** 2).sort_values().index[:num_terms].values,
            'top_left': ((df.x + 1) ** 2 + (df.y - 1) ** 2).sort_values().index[:num_terms].values,
            'right': ((df.x - 1) ** 2 + df.y ** 2).sort_values().index[:num_terms].values,
            'left': ((df.x + 1) ** 2 + df.y ** 2).sort_values().index[:num_terms].values,
            'bottom_right': ((df.x - 1) ** 2 + (df.y + 1) ** 2).sort_values().index[:num_terms].values,
            'bottom': (df.x ** 2 + (df.y + 1) ** 2).sort_values().index[:num_terms].values,
            'bottom_left': ((df.x + 1) ** 2 + (df.y + 1) ** 2).sort_values().index[:num_terms].values,
        }

    def get_term_projection(self):
        dim_term = np.matrix(self.category_counts.values) * self.projection[:, [self.x_dim, self.y_dim]]
        df = pd.DataFrame(dim_term, index=self.category_corpus.get_terms(), columns=['x', 'y'])
        return df


