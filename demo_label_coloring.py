import scattertext as st
import numpy as np
import re

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse'
).build().compact(st.AssociationCompactor(1000))

query = re.compile('.*(obama|barack|romney|mitt).*')
rep_query = re.compile('.*(romney|mitt).*')
dem_query = re.compile('.*(obama|barack).*')

term_metadata_df = corpus.get_term_freq_df('').assign(
    MatchesQuery=lambda df: np.array([query.match(word) is not None for word in df.index]),
    Frequency=lambda df: df.sum(axis=1),
    TextColor=lambda df: [
        '#1b4b5a' if dem_query.match(term) is not None
        else '#d35c37' if rep_query.match(term) is not None
        else '#d6c6b9'
        for term in df.index
    ],
    SuppressText=lambda df: df.apply(
        lambda row: not (row.MatchesQuery or row.Frequency < 30),
        axis=1
    ),
    PointColor=lambda df: df.TextColor
)

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=corpus.get_df()['speaker'],
    transform=st.Scalers.dense_rank,
    max_overlapping=3,
    term_metadata_df=term_metadata_df,
    header_names={'right': 'Most Frequent'},
    text_color_column='TextColor',
    suppress_text_column='SuppressText',
    color_column='PointColor',
    label_priority_column='MatchesQuery',
    right_order_column='Frequency'
)
fn = 'demo_label_coloring.html'
open(fn, 'w').write(html)
print('open ./%s in Chrome' % fn)
