from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_frequency_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.termscoring.ScaledFScore import ScaledFScorePresetsNeg1To1

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=whitespace_nlp_with_sentences).build()
html = produce_frequency_explorer(corpus,
                                  category='democrat',
                                  category_name='Democratic',
                                  not_category_name='Republican',
                                  minimum_term_frequency=5,
                                  width_in_pixels=1000,
                                  term_scorer=ScaledFScorePresetsNeg1To1(
	                                      beta=1,
	                                      scaler_algo='normcdf'
                                      ),
                                  grey_threshold=0,
                                  y_axis_values=[-1, 0, 1],
                                  metadata=convention_df['speaker'])
fn = './demo_scaled_f_score.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
