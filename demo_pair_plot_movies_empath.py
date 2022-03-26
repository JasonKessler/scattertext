import scattertext as st
import scattertext.categoryprojector.pairplot


movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category \
    .apply(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])

empath_feature_builder = st.FeatsFromOnlyEmpath()
corpus = st.CorpusFromPandas(
    movie_df,
    category_col='movie_name',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences,
    feats_from_spacy_doc=empath_feature_builder
).build()

html = scattertext.categoryprojector.pairplot.produce_pairplot(
    corpus,
    use_metadata=True,
    default_to_term_comparison=False,
    category_projector=st.CategoryProjector(selector=None),
    topic_model_term_lists=empath_feature_builder.get_top_model_term_lists(),
    metadata=movie_df['category'] + ': ' + movie_df['movie_name'],
    #category_metadata_df=corpus.get_df().set_index('speaker')[['party']],
    #category_color_func='(function(x) {return x.etc.party == "republican" ? "red" : "blue"})'
)

file_name = 'movie_pair_plot_empath.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
