import numpy as np
import pandas as pd


class Lowess(object):
    def __init__(self, frac=2. / 3., it=10):
        self.points = None
        self.frac = frac
        self.it = it

    def fit(self, xdata, ydata):
        import statsmodels.api as sm
        try:
            self.model = sm.nonparametric.lowess(ydata, xdata.T[0], frac=self.frac, it=self.it)
        except ValueError:
            self.model = sm.nonparametric.lowess(ydata, xdata.T, frac=self.frac, it=self.it)
        return self

    def predict(self, x):
        return np.interp(x, self.model.T[0], self.model.T[1])

    def fit_predict(self, xdata, ydata):
        df = pd.DataFrame({
            'X': np.array(xdata.T[0]),
            'Y': np.array(ydata)
        }).sort_values(by='X')

        return self.fit(df.X, df.Y).predict(xdata)
