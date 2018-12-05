import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
general_inquirer_feature_builder = st.FeatsFromGeneralInquirer()
corpus = st.CorpusFromPandas(convention_df,
                             category_col='party',
                             text_col='text',
                             nlp=st.whitespace_nlp_with_sentences,
                             feats_from_spacy_doc=general_inquirer_feature_builder).build()
html = st.produce_frequency_explorer(corpus,
                                     category='democrat',
                                     category_name='Democratic',
                                     not_category_name='Republican',
                                     metadata=convention_df['speaker'],
                                     use_non_text_features=True,
                                     use_full_doc=True,
                                     term_scorer=st.LogOddsRatioUninformativeDirichletPrior(),
                                     grey_threshold=1.96,
                                     width_in_pixels=1000,
                                     topic_model_term_lists=general_inquirer_feature_builder.get_top_model_term_lists(),
                                     metadata_descriptions=general_inquirer_feature_builder.get_definitions())
fn = 'demo_general_inquirer_frequency_plot.html'
with open(fn, 'wb') as out:
    out.write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (fn))
