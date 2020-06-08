import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
moral_foundations_feats = st.FeatsFromMoralFoundationsDictionary()
corpus = st.CorpusFromPandas(convention_df,
                             category_col='party',
                             text_col='text',
                             nlp=st.whitespace_nlp_with_sentences,
                             feats_from_spacy_doc=moral_foundations_feats).build()

cohens_d_scorer = st.CohensD(corpus).use_metadata()
term_scorer = cohens_d_scorer.set_categories('democrat', ['republican'])
mfd_df = term_scorer.get_score_df()
print(mfd_df.head())
mfd_df.to_csv('demo_moral_foundations.csv')
print('See demo_moral_foundations.csv for the output.')

html = st.produce_frequency_explorer(corpus,
                                     category='democrat',
                                     category_name='Democratic',
                                     not_category_name='Republican',
                                     metadata=convention_df['speaker'],
                                     use_non_text_features=True,
                                     use_full_doc=True,
                                     term_scorer=st.CohensD(corpus).use_metadata(),
                                     grey_threshold=0,
                                     width_in_pixels=1000,
                                     topic_model_term_lists=moral_foundations_feats.get_top_model_term_lists(),
                                     metadata_descriptions=moral_foundations_feats.get_definitions())
fn = 'demo_moral_foundations.html'
with open(fn, 'wb') as out:
    out.write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (fn))
