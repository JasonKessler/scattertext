import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category.apply(
	lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x]
)
movie_df = movie_df[movie_df.category.isin(['Negative', 'Positive'])]

corpus = (st.CorpusFromPandas(movie_df,
                              category_col='category',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())

# Remove relatively infrequent terms from both categories
corpus = corpus.select(st.ClassPercentageCompactor(term_count=2,
                                                   term_ranker=st.OncePerDocFrequencyRanker))
fn = 'demo_characteristic_chart.html'

open(fn, 'wb').write(st.produce_characteristic_explorer(
	corpus,
	category='Positive',
	not_category_name='Negative',
	metadata=corpus.get_df()['movie_name'],
	characteristic_scorer=st.DenseRankCharacteristicness(rerank_ranks=False),
	term_ranker=st.termranking.AbsoluteFrequencyRanker,
	term_scorer=st.ScaledFScorePresets(beta=1, one_to_neg_one=True)
).encode('utf-8'))
print('open ' + fn)
