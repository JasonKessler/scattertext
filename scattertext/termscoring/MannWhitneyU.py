import pandas as pd
import numpy as np
from scipy.stats import norm, mannwhitneyu, ranksums

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class MannWhitneyU(CorpusBasedTermScorer):
    '''
    Mann Whitney U test

    term_scorer = (MannWhitneyU(corpus).set_categories('Positive', ['Negative'], ['Plot']))

    html = st.produce_frequency_explorer(
        corpus,
        category='Positive',
        not_categories=['Negative'],
        neutral_categories=['Plot'],
        term_scorer=term_scorer,
        metadata=rdf['movie_name'],
        grey_threshold=0,
        show_neutral=True
    )
    file_name = 'rotten_fresh_mwu.html'
    open(file_name, 'wb').write(html.encode('utf-8'))
    IFrame(src=file_name, width=1300, height=700)
    '''

    def _set_scorer_args(self, **kwargs):
        pass

    def get_scores(self, *args):
        return self.get_score_df()['mwu_z']

    def get_score_df(self, correction_method=None):
        '''
        Computes Mann Whitney corrected p, z-values.  Falls back to normal approximation when numerical limits are reached.

        :param correction_method: str or None, correction method from statsmodels.stats.multitest.multipletests
         'fdr_bh' is recommended.
        :return: pd.DataFrame
        '''
        X = self._get_X().astype(np.float64)
        X = X / X.sum(axis=1)
        cat_X, ncat_X = self._get_cat_and_ncat(X)

        def normal_apx(u, x, y):
            # from https://stats.stackexchange.com/questions/116315/problem-with-mann-whitney-u-test-in-scipy
            m_u = len(x) * len(y) / 2
            sigma_u = np.sqrt(len(x) * len(y) * (len(x) + len(y) + 1) / 12)
            z = (u - m_u) / sigma_u
            return 2*norm.cdf(z)
        scores = []
        for i in range(cat_X.shape[1]):
            cat_list = cat_X.T[i].A1
            ncat_list = ncat_X.T[i].A1
            try:
                if cat_list.mean() > ncat_list.mean():
                    mw = mannwhitneyu(cat_list, ncat_list, alternative='greater')
                    if mw.pvalue in (0, 1):
                        mw.pvalue = normal_apx(mw.staistic, cat_list, ncat_list)

                    scores.append({'mwu': mw.statistic, 'mwu_p': mw.pvalue, 'mwu_z': norm.isf(float(mw.pvalue)), 'valid':True})

                else:
                    mw = mannwhitneyu(ncat_list, cat_list, alternative='greater')
                    if mw.pvalue in (0, 1):
                        mw.pvalue = normal_apx(mw.staistic, ncat_list, cat_list)

                    scores.append({'mwu': -mw.statistic, 'mwu_p': 1 - mw.pvalue, 'mwu_z': 1. - norm.isf(float(mw.pvalue)), 'valid':True})
            except:
                scores.append({'mwu': 0, 'mwu_p': 0, 'mwu_z': 0, 'valid':False})

        score_df = pd.DataFrame(scores, index=self.corpus_.get_terms()).fillna(0)
        if correction_method is not None:
            from statsmodels.stats.multitest import multipletests
            for method in ['mwu']:
                valid_pvals = score_df[score_df.valid].mwu_p
                valid_pvals_abs = np.min([valid_pvals, 1-valid_pvals], axis=0)
                valid_pvals_abs_corr = multipletests(valid_pvals_abs, method=correction_method)[1]
                score_df[method + '_p_corr'] = 0.5

                valid_pvals_abs_corr[valid_pvals > 0.5] = 1. - valid_pvals_abs_corr[valid_pvals > 0.5]
                valid_pvals_abs_corr[valid_pvals < 0.5] = valid_pvals_abs_corr[valid_pvals < 0.5]
                score_df.loc[score_df.valid, method + '_p_corr'] = valid_pvals_abs_corr
                score_df[method + '_z'] = -norm.ppf(score_df[method + '_p_corr'])
        return score_df

    def get_name(self):
        return "Mann Whitney Z"
