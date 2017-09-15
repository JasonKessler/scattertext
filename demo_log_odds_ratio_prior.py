import numpy as np
import spacy

from scattertext import SampleCorpora, LogOddsRatioUninformativeDirichletPrior
from scattertext import produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.Scalers import scale_neg_1_to_1_with_zero_mean_abs_max, scale

nlp = spacy.en.English()
convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=nlp).build()

term_freq_df = corpus.get_term_freq_df()
frequencies_scaled = scale(np.log(term_freq_df.sum(axis=1).values))
zeta_i_j = (LogOddsRatioUninformativeDirichletPrior()
            .get_zeta_i_j_given_separate_counts(term_freq_df['democrat freq'],
                                                term_freq_df['republican freq']))
zeta_scaled_for_charting = scale_neg_1_to_1_with_zero_mean_abs_max(zeta_i_j)

html = produce_scattertext_explorer(corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    minimum_term_frequency=5,
                                    width_in_pixels=1000,
                                    x_coords=frequencies_scaled,
                                    y_coords=zeta_scaled_for_charting,
                                    scores=zeta_i_j,
                                    sort_by_dist=False,
                                    metadata=convention_df['speaker'],
                                    x_label='Log Frequency',
                                    y_label='Log Odds Ratio w/ Prior (a_w=0.01)')
file_name = 'demo_log_odds_ratio_prior.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)
