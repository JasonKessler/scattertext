import pacmap

import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category \
    .apply(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])

corpus = st.CorpusFromPandas(
    movie_df,
    category_col='movie_name',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build().get_stoplisted_unigram_corpus()


category_projection = st.CategoryProjector(
    projector=pacmap.PaCMAP(n_dims=2, n_neighbors=None, MN_ratio=0.5, FP_ratio=2.0),
    fit_transform_kwargs={'init':'pca'}
).project(corpus)

html = st.produce_pairplot(
    corpus,
    category_projection=category_projection,
    metadata=movie_df['category'] + ': ' + movie_df['movie_name'],
    scaler=st.Scalers.scale_0_to_1,
    show_halo=True,
    default_to_term_comparison=False
)

file_name = 'movie_pair_plot_pacmap.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
