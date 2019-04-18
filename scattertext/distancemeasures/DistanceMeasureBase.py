class DistanceMeasureBase(object):
    @staticmethod
    def distances(fixed_x, fixed_y, x_vec, y_vec):
        '''

        :param fixed_x: float
        :param fixed_y: float
        :param x_vec: np.array[float]
        :param y_vec: np.array[float]
        :return: np.array[float]
        '''
        raise NotImplementedError()