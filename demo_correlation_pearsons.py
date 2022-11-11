from sklearn.svm import LinearSVC

import scattertext as st

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse'
).build()

X = corpus.get_term_doc_mat()
y = corpus.get_category_ids()

clf = LinearSVC()
clf.fit(X=X, y=y==corpus.get_categories().index('democrat'))

compactcorpus = corpus.get_unigram_corpus().compact(st.AssociationCompactor(2000))

correlation_df = st.Correlations().set_correlation_type(
    'pearsonr'
).get_correlation_df(
    corpus=compactcorpus,
    document_scores=clf.decision_function(X=X)
).reindex(compactcorpus.get_terms())

print(correlation_df)


plot_df = correlation_df.assign(
    X=lambda df: df.Frequency,
    Y=lambda df: df['r'],
    Xpos=lambda df: st.Scalers.dense_rank(df.X),
    Ypos=lambda df: st.Scalers.scale_center_zero_abs(df.Y),
    SuppressDisplay=False,
    ColorScore=lambda df: df.Ypos,
)

html = st.dataframe_scattertext(
    compactcorpus,
    plot_df=plot_df,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    width_in_pixels=1000,
    metadata=lambda c: c.get_df()['speaker'],
    unified_context=False,
    ignore_categories=False,
    color_score_column='ColorScore',
    left_list_column='ColorScore',
    y_label="Pearson r (correlation to SVM document score)",
    x_label='Frequency Ranks',
    header_names={'upper': 'Top Democratic',
                  'lower': 'Top Republican'},
)

open('svm_correlation_pearsons.html', 'w').write(html)
print('open ./svm_correlation_pearsons.html')
