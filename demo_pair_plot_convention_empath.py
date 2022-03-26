import scattertext as st
import scattertext.categoryprojector.pairplot

convention_df = st.SampleCorpora.ConventionData2012.get_data()
empath_feature_builder = st.FeatsFromOnlyEmpath()

corpus = st.CorpusFromPandas(
    convention_df,
    category_col='speaker',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences,
    feats_from_spacy_doc=empath_feature_builder).build().get_unigram_corpus()

html = scattertext.categoryprojector.pairplot.produce_pairplot(
    corpus,
    use_metadata=True,
    default_to_term_comparison=False,
    category_projector=st.CategoryProjector(selector=None),
    topic_model_term_lists=empath_feature_builder.get_top_model_term_lists(),
    metadata=convention_df['party'] + ': ' + convention_df['speaker'],
    category_metadata_df=corpus.get_df().set_index('speaker')[['party']],
    category_color_func='(function(x) {return x.etc.party == "republican" ? "red" : "blue"})'
)

file_name = 'convention_pair_plot_empath.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
