import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                              category_col='party',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus()
          .remove_infrequent_words(3, term_ranker=st.OncePerDocFrequencyRanker))

term_scorer = (st.BNSScorer(corpus).set_categories('democrat'))
print(term_scorer.get_score_df().sort_values(by='democrat BNS'))

html = st.produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    scores=term_scorer.get_score_df()['democrat BNS'].reindex(corpus.get_terms()).values,
    metadata=lambda c: c.get_df()['speaker'],
    minimum_term_frequency=0,
    grey_threshold=0,
    y_label=f'BNS (alpha={term_scorer.prior_counts})'
)
open('bi_normal_separation.html', 'w').write(html)
print('./open bi_normal_separation.html')
