import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category.apply\
	(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])
corpus = st.CorpusFromPandas(
	movie_df,
	category_col='category',
	text_col='text',
	nlp=st.whitespace_nlp_with_sentences
).build()
corpus = corpus.get_unigram_corpus()

semiotic_square = st.SemioticSquare(
	corpus,
	category_a='Positive',
	category_b='Negative',
	neutral_categories=['Plot'],
	scorer=st.RankDifference()
)

html = st.produce_semiotic_square_explorer(semiotic_square,
                                           category_name='Positive',
                                           not_category_name='Negative',
                                           x_label='Fresh-Rotten',
                                           y_label='Plot-Review',
                                           neutral_category_name='Plot Description',
                                           metadata=movie_df['movie_name'])

fn = 'demo_semiotic.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
