import scattertext as st

fn = 'rotten_fresh2.html'
df = st.SampleCorpora.RottenTomatoes.get_data()
corpus = (st.CorpusFromPandas(df,
                              category_col='category',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
	.build())
term_scorer = (st.LORIDPFactory(corpus,
                                category='fresh',
                                not_categories=['rotten'],
                                starting_count=1,
                                alpha=10)
	.use_general_term_frequencies()
	.use_all_categories()
	.get_term_scorer())
tdf = corpus.get_term_freq_df()
(open(fn, 'wb')
	.write(
	st.produce_fightin_words_explorer(
		corpus,
		category='fresh',
		not_categories=['rotten'],
		metadata=df['movie_name'],
		term_scorer=term_scorer,
		transform=st.Scalers.percentile_dense)
		.encode('utf-8'))
)
print(fn)
