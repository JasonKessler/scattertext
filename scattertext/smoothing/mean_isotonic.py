import pandas as pd
import numpy as np
from sklearn.isotonic import IsotonicRegression


class MeanIsotonic:
    def __init__(self, n=1000):
        self.n = n

    def fit(self, xdata, ydata):
        assert len(xdata.T[0]) == len(ydata)
        df = pd.DataFrame({
            'x': xdata.T[0],
            'y': ydata
        })

        # Average runs of isotonic regression
        pred = np.zeros(len(df), dtype=np.float)
        for i in range(self.n):
            sample_df = df.sample(frac=0.5)
            pred += 1 / self.n * IsotonicRegression(
                y_max=1, y_min=0, out_of_bounds='clip'
            ).fit(sample_df.x.values, sample_df.y.values).predict(df.x.values)
        self.output = pred
        return self

    def predict(self, x):
        # This is awful and needs to be fixed. To do: fix.
        return np.array([self.output]).T
        #return np.interp(x, self.model.T[0], self.model.T[1])

    def fit_predict(self, x, y):
        assert len(x) == len(y)
        df = pd.DataFrame({
            'x': x,
            'y': y
        })

        # Average runs of isotonic regression
        pred = np.zeros(len(df), dtype=np.float)
        for i in range(self.n):
            sample_df = df.sample(frac=0.5)
            pred += 1 / self.n * IsotonicRegression(
                y_max=1, y_min=0, out_of_bounds='clip'
            ).fit(sample_df.x.values, sample_df.y.values).predict(df.x.values)
        return pred

