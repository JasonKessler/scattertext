import scattertext as st
import scattertext.categoryprojector.pairplot

convention_df = st.SampleCorpora.ConventionData2012.get_data()
general_inquirer_feature_builder = st.FeatsFromGeneralInquirer()

corpus = st.CorpusFromPandas(
    convention_df,
    category_col='speaker',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences,
    feats_from_spacy_doc=general_inquirer_feature_builder,
).build().get_unigram_corpus()

html = scattertext.categoryprojector.pairplot.produce_pairplot(
    corpus,
    use_metadata=True,
    category_projector=st.CategoryProjector(selector=None),
    topic_model_term_lists=general_inquirer_feature_builder.get_top_model_term_lists(),
    topic_model_preview_size=100,
    metadata_descriptions=general_inquirer_feature_builder.get_definitions(),
    metadata=convention_df['party'] + ': ' + convention_df['speaker']
)

file_name = 'convention_pair_plot_geninq.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
