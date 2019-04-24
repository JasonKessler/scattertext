import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()

corpus = st.CorpusFromPandas(
    movie_df,
    category_col='category',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build()
corpus = corpus.get_unigram_corpus()

fwer_method = 'fdr_bh'

x_score_df = st.MannWhitneyU(corpus).set_categories('fresh', ['rotten']).get_score_df(fwer_method)
y_score_df = st.MannWhitneyU(corpus).set_categories('plot', ['fresh', 'rotten']).get_score_df(fwer_method)


labels = {'not_a_and_not_b': 'Reviews',
          'a_and_b': 'Plot Descriptions',
          'a_and_not_b': 'Negative',
          'b_and_not_a': 'Positive',
          'a': '',
          'b': '',
          'not_a': '',
          'not_b': ''}

html = st.produce_two_axis_plot(corpus, x_score_df, y_score_df, 'fresh', 'plot',
                                x_tooltip_label='rotten-fresh',
                                y_tooltip_label='plot-review',
                                statistic_column='mwu_z',
                                p_value_column='mwu_p',
                                statistic_name='z',
                                semiotic_square_labels=labels)

fn = 'demo_two_axes.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
