from functools import partial

from scipy.optimize import leastsq


def fitfunc(p, x):
    return p[0] + p[1] * (x ** p[2])


def errfunc(p, x, y):
    return y - fitfunc(p, x)


class PowerLaw(object):
    def __init__(self):
        pass

    def fit(self, xdata, ydata):
        params, _ = leastsq(errfunc, [max(ydata), -1, -0.5], args=(xdata, ydata), maxfev=500)
        return partial(fitfunc, params)
