import numpy as np

from scattertext.termscoring.CohensDCalculator import CohensDCalculator
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class CohensD(CorpusBasedTermScorer, CohensDCalculator):
    '''
    Cohen's d scores

    term_scorer = (CohensD(corpus).set_categories('Positive', ['Negative'], ['Plot']))

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
    file_name = 'rotten_fresh_fre.html'
    open(file_name, 'wb').write(html.encode('utf-8'))
    IFrame(src=file_name, width=1300, height=700)
    '''

    def _set_scorer_args(self, **kwargs):
        pass

    def get_scores(self, *args):
        return self.get_score_df()['cohens_d']

    def get_score_df(self, correction_method=None):
        '''

        :param correction_method: str or None, correction method from statsmodels.stats.multitest.multipletests
         'fdr_bh' is recommended.
        :return: pd.DataFrame
        '''
        # From https://people.kth.se/~lang/Effect_size.pdf
        # Shinichi Nakagawa1 and Innes C. Cuthill. Effect size, confidence interval and statistical
        # significance: a practical guide for biologists. 2007. In Biological Reviews 82.
        #
        # Modification: when calculating variance, an empty document is added to each set
        X = self._get_X().astype(np.float64)
        X_doc_len_norm = X / X.sum(axis=1)
        X_doc_len_norm[np.isnan(X_doc_len_norm)] = 0
        cat_X, ncat_X = self._get_cat_and_ncat(X_doc_len_norm)
        orig_cat_X, orig_ncat_X = self._get_cat_and_ncat(X)
        score_df = (self
                    .get_cohens_d_df(cat_X, ncat_X, orig_cat_X, orig_ncat_X, correction_method)
                    .set_index(np.array(self._get_index())))
        return score_df


    def get_name(self):
        return "Cohen's d"


class HedgesR(CohensD):
    def get_scores(self, *args):
        return self.get_score_df()['hedges_r']

    def get_name(self):
        return "Hedge's r"
