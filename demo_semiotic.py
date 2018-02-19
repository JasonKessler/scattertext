import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
#movie_df.category = movie_df.category.apply \
#(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])
corpus = st.CorpusFromPandas(
	movie_df,
	category_col='category',
	text_col='text',
	nlp=st.whitespace_nlp_with_sentences
).build()
corpus = corpus.get_unigram_corpus()

semiotic_square = st.SemioticSquare(
	corpus,
	category_a='fresh',
	category_b='rotten',
	neutral_categories=['plot'],
	scorer=st.RankDifference(),
	labels={'not_a_and_not_b': 'Plot Descriptions',
	        'a_and_b': 'Reviews',
	        'a_and_not_b': 'Positive',
	        'b_and_not_a': 'Negative',
	        'a':'',
	        'b':'',
	        'not_a':'',
	        'not_b':''}
)

html = st.produce_semiotic_square_explorer(semiotic_square,
                                           category_name='fresh',
                                           not_category_name='rotten',
                                           x_label='Fresh-Rotten',
                                           y_label='Plot-Review',
                                           num_terms_semiotic_square=20,
                                           neutral_category_name='Plot Description',
                                           metadata=movie_df['movie_name'])

fn = 'demo_semiotic.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
