import spacy

from scattertext import SampleCorpora, produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.termscoring.LogOddsUniformativePriorScore import LogOddsUninformativePriorScore

nlp = spacy.en.English()
convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=nlp).build()
term_freq_df = corpus.get_term_freq_df()
scores = -(LogOddsUninformativePriorScore
           .get_thresholded_score(term_freq_df['democrat freq'],
                                  term_freq_df['republican freq'],
                                  alpha_w=2.,
                                  threshold=0.05))
html = produce_scattertext_explorer(corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    scores=scores,
                                    sort_by_dist=False,
                                    grey_zero_scores=True,
                                    minimum_term_frequency=5,
                                    pmi_filter_thresold=4,
                                    width_in_pixels=1000,
                                    metadata=convention_df['speaker'])
open('./demo_insignificant_greyed_out.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_insignificant_greyed_out.html in Chrome or Firefox.')
