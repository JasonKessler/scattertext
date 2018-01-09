import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()

corpus = st.CorpusFromPandas(
	movie_df,
	category_col='category',
	text_col='text',
	nlp=st.whitespace_nlp_with_sentences
).build().get_unigram_corpus()

semiotic_square = st.SemioticSquare(
	corpus,
	category_a='fresh',
	category_b='rotten',
	neutral_categories=['plot'],
	scorer=st.LogOddsRatioUninformativeDirichletPrior(alpha_w=0.001)
)

html = st.produce_semiotic_square_explorer(semiotic_square,
                                           jitter=0.01,
                                           category_name='Fresh',
                                           not_category_name='Rotten',
                                           x_label='Rotten-Fresh',
                                           y_label='Plot-Review',
                                           neutral_category_name='Plot Description',
                                           metadata=movie_df['movie_name'],
                                           x_axis_values=[-2.58, -1.96, 0, 1.96, 2.58],
                                           y_axis_values=[-2.58, -1.96, 0, 1.96, 2.58])

fn = 'demo_semiotic.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
