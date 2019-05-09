import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                           category_col='speaker',
                           text_col='text',
                           nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())
html = st.produce_frequency_explorer(
    corpus,
    category='BARACK OBAMA',
    term_scorer=st.ScaledFScorePresets(one_to_neg_one=True, use_score_difference=True),
    metadata=convention_df['speaker'],
    grey_threshold=0
)
file_name = 'demo_obama.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
