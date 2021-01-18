import statsmodels.api as sm
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

html = st.dataframe_scattertext(
    corpus,
    plot_df=dispersion_df,
    metadata=corpus.get_df()['speaker'] + ' (' + corpus.get_df()['party'].str.upper() + ')',
    ignore_categories=True,
    x_label='Log Frequency',
    y_label="Rosengren's S",
    y_axis_labels=['More Dispersion', 'Medium', 'Less Dispersion'],
)

fn = 'demo_dispersion_basic.html'
open(fn, 'w').write(html)
print('open ./%s in Chrome' % fn)
