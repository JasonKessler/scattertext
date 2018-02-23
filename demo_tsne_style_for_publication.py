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
                                      color_func='''(function(d) {return d.s > 0.5 ? d3.interpolateRdYlBu(0.6) : d3.interpolateRdYlBu(0.4) })''',
                                      center_label_over_points = True,
                                      censor_points=True,
                                      width_in_pixels=1000)
file_name = 'demo_tsne_style_for_publication.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open', file_name, 'in chrome')
