import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                              category_col='speaker',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
          .build().get_unigram_corpus())

html = st.produce_scattertext_explorer(
    corpus,
    category='BARACK OBAMA',
    sort_by_dist=False,
    metadata=convention_df['party'] + ': ' + convention_df['speaker'],
    term_scorer=st.RankDifference(),
    transform=st.Scalers.dense_rank
)
file_name = 'demo_dense_rank_difference.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
