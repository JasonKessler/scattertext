import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()

corpus = st.CorpusFromPandas(
    movie_df,
    category_col='category',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build().get_unigram_corpus()

beta_posterior = st.BetaPosterior(corpus).set_categories('fresh', ['rotten'])
score_df = beta_posterior.get_score_df()
print("Top Fresh Terms")
print(score_df.sort_values(by='cat_p').head())

print("Top Rotten Terms")
print(score_df.sort_values(by='ncat_p').head())

html = st.produce_frequency_explorer(
    corpus,
    category='fresh',
    not_category_name='rotten',
    term_scorer=beta_posterior,
    grey_threshold=1.96
)

file_name = 'demo_beta_posterior.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)

