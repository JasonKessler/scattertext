try:
    import phate
except:
    print('Install phate using $ pip install -U phate matplotlib')
    exit(1)


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

html = st.produce_pairplot(
    corpus,
    category_projector=st.CategoryProjector(projector=phate.PHATE()),
    metadata=movie_df['category'] + ': ' + movie_df['movie_name'],
    #scaler=st.Scalers.scale_0_to_1,
    #show_halo=False,
    #d3_url_struct=st.D3URLs(
    #    d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
    #    d3_url='scattertext/data/viz/scripts/d3.min.js'
    #),
    default_to_term_comparison=False
)

file_name = 'movie_pair_plot_phates.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
