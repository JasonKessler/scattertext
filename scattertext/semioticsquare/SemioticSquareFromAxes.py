import numpy as np
import pandas as pd

from scattertext.distancemeasures.EuclideanDistance import EuclideanDistance
from scattertext.semioticsquare.SemioticSquare import SemioticSquareBase


class SemioticSquareFromAxes(SemioticSquareBase):
    def __init__(self,
                 term_doc_matrix,
                 axes,
                 x_axis_name,
                 y_axis_name,
                 labels=None,
                 distance_measure=EuclideanDistance):

        '''

        :param term_doc_matrix: TermDocMatrix
        :param axes: pd.DataFrame
        :param x_axis_name: str
        :param y_axis_name: str
        :param labels: dict, optional
        :param distance_measure: DistanceMeasureBase, EuclideanDistance by default
        '''
        self.term_doc_matrix = term_doc_matrix
        assert type(axes) == pd.DataFrame
        assert set(axes.columns) == set(['x', 'y'])
        assert set(axes.index) == set(term_doc_matrix.get_terms())
        self.axes = axes
        self.y_axis_name = y_axis_name
        self.x_axis_name = x_axis_name
        if labels is None:
            self._labels = {}
        else:
            self._labels = labels
        self._distance_measure = distance_measure
    def get_labels(self):
        '''

        :return: dict
        '''
        default_labels = {'a': 'not-%s; %s' % (self.x_axis_name, self.y_axis_name),
                          'not_a': '%s; not-%s' % (self.x_axis_name, self.y_axis_name),
                          'b': '%s; %s' % (self.x_axis_name, self.y_axis_name),
                          'not_b': 'not-%s; not-%s' % (self.x_axis_name, self.y_axis_name),
                          'a_and_b': '%s' % (self.y_axis_name),
                          'not_a_and_not_b': 'not-%s' % (self.y_axis_name),
                          'a_and_not_b': 'not-%s' % (self.x_axis_name),
                          'b_and_not_a': '%s' % (self.x_axis_name)}
        return {name + '_label': self._labels.get(name, default_labels[name]) for name in default_labels}

    def get_axes(self, **kwargs):
        return self.axes

    def get_lexicons(self, num_terms=10):
        x_max = self.axes['x'].max()
        x_med = self.axes['x'].median()
        x_min = self.axes['x'].min()
        y_max = self.axes['y'].max()
        y_med = self.axes['y'].median()
        y_min = self.axes['y'].min()

        lexicons = {}
        for label, [x_coord, y_coord] in [
            ['a', [x_min, y_max]],
            ['not_a', [x_max, y_min]],
            ['b', [x_max, y_max]],
            ['not_b', [x_min, y_min]],
            ['a_and_b', [x_med, y_max]],
            ['not_a_and_not_b', [x_med, y_min]],
            ['b_and_not_a', [x_max, y_med]],
            ['a_and_not_b', [x_min, y_med]],
        ]:
            #scores = np.linalg.norm(np.array([self.axes['x'] - x_coord, self.axes['y'] - y_coord]), 2, axis=0)
            scores = self._distance_measure.distances(x_coord, y_coord, self.axes['x'], self.axes['y'])
            lexicons[label] = list(self.axes.index[np.argsort(scores)])[:num_terms]
        return lexicons
