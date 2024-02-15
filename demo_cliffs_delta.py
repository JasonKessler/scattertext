import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                           category_col='party',
                           text_col='text',
                           nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())

html = st.produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    term_scorer=st.CliffsDelta(corpus),
    metadata=convention_df['speaker'],
    horizontal_line_y_position=0,
    grey_threshold=0
)
file_name = 'demo_cliffs_delta.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./demo_cliffs_delta.html in Chrome or Firefox.')
