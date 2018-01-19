from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_fightin_words_explorer, \
	ScaledFScoreSignificance
from scattertext.CorpusFromPandas import CorpusFromPandas

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=whitespace_nlp_with_sentences).build()

html = produce_fightin_words_explorer(corpus,
                                      category='democrat',
                                      category_name='Democratic',
                                      not_category_name='Republican',
                                      minimum_term_frequency=5,
                                      width_in_pixels=1000,
                                      term_scorer=ScaledFScoreSignificance(
	                                      beta=0.5, scaler_algo='percentiledense'),
                                      metadata=convention_df['speaker'])
open('./demo_scaled_f_score.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_scaled_f_score.html in Chrome or Firefox.')
