from transformers import RobertaTokenizerFast
import scattertext as st

tokenizer_fast = RobertaTokenizerFast.from_pretrained(
    "roberta-base", add_prefix_space=True)
tokenizer = st.RobertaTokenizerWrapper(tokenizer_fast)

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse = lambda df: df.text.apply(tokenizer.tokenize)
)

corpus = st.OffsetCorpusFactory(
    df,
    category_col='party',
    parsed_col='parse',
    feat_and_offset_getter=st.TokenFeatAndOffsetGetter()
).build()

# Remove words occur less than 5 times
corpus = corpus.remove_infrequent_words(5, non_text=True)

plot_df = corpus.get_metadata_freq_df('').assign(
    Y=lambda df: df.democrat,
    X=lambda df: df.republican,
    Ypos=lambda df: st.Scalers.dense_rank(df.Y),
    Xpos=lambda df: st.Scalers.dense_rank(df.X),
    SuppressDisplay=False,
    ColorScore=lambda df: st.Scalers.scale_center_zero(df.Ypos - df.Xpos),
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
    y_label='Democarats',
    x_label='Republicans',
    header_names={'upper': 'Top Democratic', 'lower': 'Top Republican', 'right': 'Most Frequent'},
    subword_encoding='RoBERTa'
)

fn = 'roberta_sentence_piece.html'
with open(fn, 'w') as of:
    of.write(html)

print("Open ./" + fn + ' in Chrome.')
