import numpy as np
import pandas as pd
from scipy.stats import norm


class CohensDCalculator(object):
    def get_cohens_d_df(self, cat_X, ncat_X, orig_cat_X, orig_ncat_X, correction_method=None):
        empty_cat_X_smoothing_doc = np.zeros((1, cat_X.shape[1]))
        empty_ncat_X_smoothing_doc = np.zeros((1, ncat_X.shape[1]))
        smoothed_cat_X = np.vstack([empty_cat_X_smoothing_doc, cat_X])
        smoothed_ncat_X = np.vstack([empty_ncat_X_smoothing_doc, ncat_X])
        n1, n2 = float(smoothed_cat_X.shape[0]), float(smoothed_ncat_X.shape[0])
        n = n1 + n2
        #print(cat_X.shape, type(cat_X))
        m1 = cat_X.mean(axis=0).A1 if type(cat_X) == np.matrix else cat_X.mean(axis=0)
        m2 = ncat_X.mean(axis=0).A1 if type(ncat_X) == np.matrix else ncat_X.mean(axis=0)
        v1 = smoothed_cat_X.var(axis=0).A1 if type(smoothed_cat_X) == np.matrix else smoothed_cat_X.mean(axis=0)
        v2 = smoothed_ncat_X.var(axis=0).A1 if type(smoothed_ncat_X) == np.matrix else smoothed_ncat_X.mean(axis=0)
        s_pooled = np.sqrt(((n2 - 1) * v2 + (n1 - 1) * v1) / (n - 2.))
        cohens_d = (m1 - m2) / s_pooled
        cohens_d_se = np.sqrt(((n - 1.) / (n - 3)) * (4. / n) * (1 + np.square(cohens_d) / 8.))
        cohens_d_z = cohens_d / cohens_d_se
        cohens_d_p = norm.sf(cohens_d_z)
        hedges_r = cohens_d * (1 - 3. / ((4. * (n - 2)) - 1))
        hedges_r_se = np.sqrt(n / (n1 * n2) + np.square(hedges_r) / (n - 2.))
        hedges_r_z = hedges_r / hedges_r_se
        hedges_r_p = norm.sf(hedges_r_z)
        score_df = pd.DataFrame({
            'cohens_d': cohens_d,
            'cohens_d_se': cohens_d_se,
            'cohens_d_z': cohens_d_z,
            'cohens_d_p': cohens_d_p,
            'hedges_r': hedges_r,
            'hedges_r_se': hedges_r_se,
            'hedges_r_z': hedges_r_z,
            'hedges_r_p': hedges_r_p,
            'm1': m1,
            'm2': m2,
            'count1': orig_cat_X.sum(axis=0).A1,
            'count2': orig_ncat_X.sum(axis=0).A1,
            'docs1': (orig_cat_X > 0).sum(axis=0).A1,
            'docs2': (orig_ncat_X > 0).sum(axis=0).A1,
        }).fillna(0)
        if correction_method is not None:
            from statsmodels.stats.multitest import multipletests
            score_df['hedges_r_p_corr'] = 0.5
            for method in ['cohens_d', 'hedges_r']:
                score_df[method + '_p_corr'] = 0.5
                pvals = score_df.loc[(score_df['m1'] != 0) | (score_df['m2'] != 0), method + '_p']
                pvals = np.min(np.array([pvals, 1. - pvals])) * 2.
                score_df.loc[(score_df['m1'] != 0) | (score_df['m2'] != 0), method + '_p_corr'] = (
                    multipletests(pvals, method=correction_method)[1]
                )
        return score_df