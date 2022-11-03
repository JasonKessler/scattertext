import spacy
import scattertext as st

nlp = spacy.load('en_core_web_sm')

convention_df = st.SampleCorpora.ConventionData2012.get_data().assign(
    Parse=lambda df: [x for x in nlp.pipe(df.text)]
)

corpus_no_cat = st.CorpusWithoutCategoriesFromParsedDocuments(
    convention_df,
    parsed_col='Parse'
).build()

compact_corpus_no_cat = corpus_no_cat.get_stoplisted_unigram_corpus().remove_infrequent_words(9)

plot_df = st.whole_corpus_productivity_scores(corpus_no_cat).assign(
    RankDelta = lambda df: st.RankDifference().get_scores(
        a=df.Productivity,
        b=df.Frequency
    )
).reindex(
    compact_corpus_no_cat.get_terms()
).dropna().assign(
    X=lambda df: df.Frequency,
    Xpos=lambda df: st.Scalers.log_scale(df.Frequency),
    Y=lambda df: df.RankDelta,
    Ypos=lambda df: st.Scalers.scale(df.RankDelta),
)



html = st.dataframe_scattertext(
    compact_corpus_no_cat.whitelist_terms(plot_df.index),
    plot_df=plot_df,
    metadata=lambda df: df.get_df()['speaker'],
    ignore_categories=True,
    x_label='Rank Frequency',
    y_label="Productivity",
    left_list_column='Ypos',
    color_score_column='Ypos',
    y_axis_labels=['Least Productive', 'Average Productivity', 'Most Productive'],
    header_names={'upper': 'Most Productive', 'lower': 'Least Productive', 'right': 'Charachteristic'},
    d3_scale_chromatic_url='../scattertext/scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
    d3_url='../scattertext/scattertext/data/viz/scripts/d3.min.js'
)

fn = 'convention_single_category_productivity.html'
open(fn, 'w').write(html)
print('open ./%s' % fn)
