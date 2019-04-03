import umap
from sklearn.feature_extraction.text import TfidfTransformer

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
    selector=None,
    normalizer=TfidfTransformer(),
    projector=umap.UMAP(min_dist=0.5, metric='cosine')
).project(corpus)

html = st.produce_pairplot(
    corpus,
    # category_projection=st.get_optimal_category_projection(corpus, verbose=True),
    category_projection=category_projection,
    metadata=movie_df['category'] + ': ' + movie_df['movie_name'],
    scaler=st.Scalers.scale_0_to_1,
    show_halo=False,
    d3_url_struct=st.D3URLs(
        d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
        d3_url='scattertext/data/viz/scripts/d3.min.js'
    )
)

file_name = 'movie_pair_plot_umap.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
