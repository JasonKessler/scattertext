import numpy as np
from scipy.optimize import leastsq


def fitfunc(p, x):
    return p[0] + p[1] * (x ** p[2])


def errfunc(p, x, y):
    return np.power(y - fitfunc(p, x), 2)


class PowerLaw(object):
    def __init__(self):
        self.partial_func = None

    def fit(self, xdata, ydata):
        self.params, _ = leastsq(errfunc, [max(ydata), -1, -0.5], args=(xdata, ydata), maxfev=500)
        return self

    def predict(self, x):
        return fitfunc(self.params, x)
