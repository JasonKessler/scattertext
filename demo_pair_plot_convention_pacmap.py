from pacmap import PaCMAP

import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()

corpus = st.CorpusFromPandas(
    convention_df,
    category_col='speaker',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build().get_stoplisted_unigram_corpus()

category_projection = st.CategoryProjector(
    projector=PaCMAP(n_dims=2, n_neighbors=None, MN_ratio=0.5, FP_ratio=2.0),
    fit_transform_kwargs={'init': 'pca'}
).project(corpus)

html = st.produce_pairplot(
    corpus,
    category_projection=category_projection,
    metadata=convention_df['party'] + ': ' + convention_df['speaker'],
    scaler=st.Scalers.scale_0_to_1,
    show_halo=True,
    default_to_term_comparison=False,
    category_metadata_df=corpus.get_df().set_index('speaker')[['party']],
    category_color_func='(function(x) {return x.etc.party == "republican" ? "red" : "blue"})'
)

file_name = 'convention_pairplot_pacmap.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
