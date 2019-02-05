import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
empath_feature_builder = st.FeatsFromOnlyEmpath()

corpus = st.CorpusFromPandas(
    convention_df,
    category_col='speaker',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences,
    feats_from_spacy_doc=empath_feature_builder).build().get_unigram_corpus()

html = st.produce_pairplot(corpus,
                           use_metadata=True,
                           category_projector=st.CategoryProjector(compactor=None),
                           topic_model_term_lists=empath_feature_builder.get_top_model_term_lists(),
                           metadata=convention_df['party'] + ': ' + convention_df['speaker'])

file_name = 'convention_pair_plot_empath.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
