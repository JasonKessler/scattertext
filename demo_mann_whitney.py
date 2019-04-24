import scattertext as st

'''
convention_df = st.SampleCorpora.ConventionData2012.get_data()
corpus = (st.CorpusFromPandas(convention_df,
                              category_col='party',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())

term_scorer = st.MannWhitneyU(corpus).set_categories('democrat', ['republican'])
html = st.produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    y_label='Mann Whitney FDR-BH Z',
    scores=term_scorer.get_score_df('fdr_bh').mwu_z,
    metadata=convention_df['speaker'],
    grey_threshold=0
)
file_name = 'demo_mann_whitney.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)
'''

movie_df = st.SampleCorpora.RottenTomatoes.get_data()

corpus = st.CorpusFromPandas(
    movie_df,
    category_col='category',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build()
corpus = corpus.get_unigram_corpus()

score_df = st.MannWhitneyU(corpus).set_categories('plot', ['fresh', 'rotten']).get_score_df('fdr_bh')

print(score_df.sort_values(by='mwu_z', ascending=False).head())
print(score_df.sort_values(by='mwu_z', ascending=False).tail())

html = st.produce_frequency_explorer(
    corpus,
    category='plot',
    y_label='Mann Whitney FDR-BH Z',
    scores=score_df.mwu_z,
    grey_threshold=0
)

file_name = 'demo_mann_whitney.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)

