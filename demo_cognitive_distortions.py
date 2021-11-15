import scattertext as st

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse = lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.OffsetCorpusFactory(
    df,
    category_col='party',
    parsed_col='parse',
    feat_and_offset_getter=st.cognitive_distortions_offset_getter_factory()
).build()

plot_df = st.CohensD(corpus).use_metadata().set_categories(
    'democrat', ['republican']
).get_score_df(
).assign(
    N = lambda df: df.count1+df.count2,
    X=lambda df: df.N,
    Y=lambda df: df.hedges_r,
    Xpos=lambda df: st.Scalers.dense_rank(df.X),
    Ypos=lambda df: st.Scalers.scale_center_zero_abs(df.Y),
    SuppressDisplay=False,
    ColorScore=lambda df: df.Ypos,
)



html = st.dataframe_scattertext(
    corpus,
    plot_df=plot_df,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    width_in_pixels=1000,
    suppress_text_column='Display',
    metadata=corpus.get_df()['speaker'],
    use_non_text_features=True,
    ignore_categories=False,
    use_offsets=True,
    unified_context=False,
    color_score_column='ColorScore',
    left_list_column='ColorScore',
    y_label='Hedges R',
    x_label='Frequency Ranks',
    header_names={'upper': 'Top Democratic', 'lower': 'Top Republican'},
)

fn = 'cognitive_distortions.html'
with open(fn, 'w') as of:
    of.write(html)

print("Open ./" + fn + ' in Chrome.')
