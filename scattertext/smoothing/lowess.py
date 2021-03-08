import numpy as np

class Lowess(object):
    def __init__(self):
        self.points = None

    def fit(self, xdata, ydata):
        import statsmodels.api as sm
        self.model = sm.nonparametric.lowess(ydata, xdata, frac=1./3)
        return self

    def predict(self, x):
        return np.interp(x, self.model.T[0], self.model.T[1])

    def fit_predict(self, xdata, ydata):
        return self.fit(xdata, ydata).predict(xdata)
