import scattertext as st
import gensim

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category \
    .apply(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])
movie_df['parse'] = movie_df.text.apply(st.whitespace_nlp_with_sentences)


corpus = st.CorpusFromParsedDocuments(
    movie_df,
    category_col='movie_name',
    parsed_col='parse'
).build().get_stoplisted_unigram_corpus()

category_projection = st.Doc2VecCategoryProjector().project(corpus)

html = st.produce_pairplot(
    corpus,
    category_projection=category_projection,
    metadata=movie_df['category'] + ': ' + movie_df['movie_name'],
    scaler=st.Scalers.scale_0_to_1,
    d3_url_struct=st.D3URLs(
        d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
        d3_url='scattertext/data/viz/scripts/d3.min.js'
    )
)

file_name = 'movie_pair_plot_d2v.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
