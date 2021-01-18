from sklearn.neighbors import KNeighborsRegressor

import scattertext as st

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.CorpusWithoutCategoriesFromParsedDocuments(
    df, parsed_col='parse'
).build().get_unigram_corpus().remove_infrequent_words(
    minimum_term_count=6
)

dispersion = st.Dispersion(corpus)

dispersion_df = dispersion.get_df().assign(
    X=lambda df: df.Frequency,
    Xpos=lambda df: st.Scalers.log_scale(df.X),
    Y=lambda df: dispersion.rosengrens(),
    Ypos=lambda df: st.Scalers.scale(df.Y),
)

dispersion_df = dispersion_df.assign(
    Expected=lambda df: KNeighborsRegressor(n_neighbors=10).fit(
        df.X.values.reshape(-1, 1), df.Y
    ).predict(df.X.values.reshape(-1, 1)),
    Residual=lambda df: df.Y - df.Expected,
    ColorScore=lambda df: st.Scalers.scale_center_zero_abs(df.Residual)
)

html = st.dataframe_scattertext(
    corpus,
    plot_df=dispersion_df,
    metadata=corpus.get_df()['speaker'] + ' (' + corpus.get_df()['party'].str.upper() + ')',
    ignore_categories=True,
    x_label='Log Frequency',
    y_label="Rosengren's S",
    y_axis_labels=['More Dispersion', 'Medium', 'Less Dispersion'],
    color_score_column='ColorScore',
    header_names={'upper': 'Lower than Expected', 'lower': 'More than Expected'},
    left_list_column='Residual',
    background_color='#e5e5e3'
)

fn = 'demo_dispersion.html'
open(fn, 'w').write(html)
print('open ./%s in Chrome' % fn)
