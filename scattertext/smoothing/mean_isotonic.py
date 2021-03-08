import pandas as pd
import numpy as np
from sklearn.isotonic import IsotonicRegression


class MeanIsotonic:
    def __init__(self, n=1000):
        self.n = n

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

