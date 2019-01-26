import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category\
	.apply(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])

corpus = st.CorpusFromPandas(
	movie_df,
	category_col='movie_name',
	text_col='text',
	nlp=st.whitespace_nlp_with_sentences
).build().get_unigram_corpus()
html = st.produce_pairplot(corpus, metadata=movie_df['category'] + ': ' + movie_df['movie_name'])

file_name = 'movie_pair_plot.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
