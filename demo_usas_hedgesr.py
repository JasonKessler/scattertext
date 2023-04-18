import sys

sys.path.insert(0, '../scattertext/')
import scattertext as st
import spacy

nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

convention_df = st.SampleCorpora.ConventionData2012.get_data().assign(
    Party=lambda df: df.party.apply(lambda x: {'democrat': 'Dem', 'republican': 'GOP'}[x]),
    Parse=lambda df: df.text.progress_apply(nlp)
)

corpus = st.OffsetCorpusFactory(
    convention_df,
    category_col='Party',
    parsed_col='Parse',
    feat_and_offset_getter=st.USASOffsetGetter(tier=1)
).build(show_progress=True)

score_df = st.CohensD(
    corpus
).use_metadata().set_categories(
    category_name='Dem'
).get_score_df(
)

plot_df = score_df.rename(columns={'hedges_r': 'HedgesR', 'hedges_r_p': 'HedgesRPval'}).assign(
    Frequency=lambda df: df.count1 + df.count2,
    X=lambda df: df.Frequency,
    Y=lambda df: df.HedgesR,
    Xpos=lambda df: st.Scalers.dense_rank(df.X),
    Ypos=lambda df: st.Scalers.scale_center_zero_abs(df.Y),
    ColorScore=lambda df: df.Ypos,
)

html = st.dataframe_scattertext(
    corpus,
    plot_df=plot_df,
    category='Dem',
    category_name='Democratic',
    not_category_name='Republican',
    width_in_pixels=1000,
    suppress_text_column='Display',
    metadata=lambda c: c.get_df()['speaker'],
    use_non_text_features=True,
    ignore_categories=False,
    use_offsets=True,
    unified_context=False,
    color_score_column='ColorScore',
    left_list_column='ColorScore',
    y_label='Hedges R',
    x_label='Frequency Ranks',
    y_axis_labels=[f'More Dem: r={plot_df.HedgesR.max():.3f}',
                   '0',
                   f'More Rep: r={-plot_df.HedgesR.max():.3f}'],
    tooltip_columns=['Frequency', 'HedgesR'],
    term_description_columns=['Frequency', 'HedgesR', 'HedgesRPval'],
    header_names={'upper': 'Top Democratic', 'lower': 'Top Republican'},
    term_word_in_term_description='Semantic Tag',
    horizontal_line_y_position=0
)

fn = 'demo_usas_level_1.html'
with open(fn, 'w') as of:
    of.write(html)
print(f'run ./open {fn}')