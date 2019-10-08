import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category.apply(lambda x: {'rotten': 'Negative',
                                                       'fresh': 'Positive',
                                                       'plot': 'Plot'}[x])
movie_df.movie_name = movie_df.movie_name.apply(lambda x: x.replace('_', ' '))

corpus = st.CorpusFromPandas(
    movie_df,
    category_col='movie_name',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build().get_stoplisted_unigram_corpus()

html = st.produce_pairplot(
    corpus,
    category_projection=st.get_optimal_category_projection(corpus, verbose=True),
    metadata=movie_df['category'] + ': ' + movie_df['movie_name'],
    d3_url_struct=st.D3URLs(
        d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
        d3_url='scattertext/data/viz/scripts/d3.min.js'
    ),
    default_to_term_comparison=False
)

file_name = 'movie_pair_plot_movies_mirror.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
