import pandas as pd
import numpy as np
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer, sparse_var


class CohensD(CorpusBasedTermScorer):
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
        return pd.Series(self.get_cohens_d_scores(), index=self._get_index())

    def get_cohens_d_scores(self):
        X = self._get_X()

        cat_X, ncat_X = self._get_cat_and_ncat(X)
        n1, n2 = cat_X.shape[1], ncat_X.shape[1]
        pooled_sd = np.sqrt(((n1 - 1) * sparse_var(cat_X) + (n2 - 1) * sparse_var(ncat_X))
                            / (n1 + n2 + 2))
        return self._get_mean_delta(cat_X, ncat_X)/pooled_sd

    def get_name(self):
        return "Cohen's d"
