import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                              category_col='party',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())

term_scorer = (st.BNSScorer(corpus, alpha=0.005).set_categories('democrat'))
print(term_scorer.get_score_df().sort_values(by='democrat'))

html = st.produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    term_scorer=term_scorer,
    metadata=lambda c: c.get_df()['speaker'],
    grey_threshold=0
)

file_name = 'demo_bi_normal_separation.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)



term_scorer = (st.BNSScorer(corpus, alpha=0.0005).set_categories('democrat'))

html = st.produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    term_scorer=term_scorer,
    metadata=lambda c: c.get_df()['speaker'],
    grey_threshold=0
)

file_name = 'demo_bi_normal_separation_0.0005.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
