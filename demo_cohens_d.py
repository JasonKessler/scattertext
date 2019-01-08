import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                           category_col='party',
                           text_col='text',
                           nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())
term_scorer = st.CohensD(corpus).set_categories('democrat', ['republican'])
print(term_scorer.get_score_df().sort_values(by='cohens_d', ascending=False).head())
html = st.produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    term_scorer=st.CohensD(corpus),
    metadata=convention_df['speaker'],
    grey_threshold=0
)
file_name = 'demo_cohens_d.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./demo_cohens_d.html in Chrome or Firefox.')
