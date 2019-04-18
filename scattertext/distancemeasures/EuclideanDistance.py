import numpy as np

from scattertext.distancemeasures.DistanceMeasureBase import DistanceMeasureBase


class EuclideanDistance(DistanceMeasureBase):
    @staticmethod
    def distances(fixed_x, fixed_y, x_vec, y_vec):
        return np.linalg.norm(np.array([x_vec - fixed_x, y_vec - fixed_y]), 2, axis=0)