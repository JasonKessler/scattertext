import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df['text'].apply(st.whitespace_nlp_with_sentences)

corpus = (st.CorpusFromParsedDocuments(convention_df,
                                       category_col='party',
                                       parsed_col='parse')
          .build().get_stoplisted_unigram_corpus())


html = st.produce_projection_explorer(corpus,
                                      category='democrat',
                                      category_name='Democratic',
                                      not_category_name='Republican',
                                      metadata=convention_df.speaker,
                                      width_in_pixels=1000)
file_name = 'demo_tsne_style.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open', file_name, 'in chrome')
