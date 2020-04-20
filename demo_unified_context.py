import scattertext as st
import pandas as pd

df = st.SampleCorpora.RottenTomatoes.get_data()
df['parse'] = df['text'].apply(st.whitespace_nlp_with_sentences)
corpus = (st.CorpusFromParsedDocuments(df, category_col='category', parsed_col='parse')
          .build()
          .get_unigram_corpus()
          .select(st.AssociationCompactor(1000)))

corpus, axes = st.EmbeddingsResolver(corpus).set_embeddings_model().project_embeddings()
term_colors = st.CategoryColorAssigner(corpus).get_term_colors()
html = st.produce_pca_explorer(
    corpus,
    category='fresh',
    not_categories=['rotten'],
    neutral_categories=['plot'],
    metadata=df['movie_name'],
    width_in_pixels=1000,
    show_axes=False,
    use_full_doc=True,
    projection=axes,
    term_colors=term_colors,
    show_characteristic=False,
    show_top_terms=False,
    unified_context=True,
    show_category_headings=True,
    show_cross_axes=False,
    include_term_category_counts=True,
    color_func="(function(d) {return modelInfo.term_colors[d.term]})",
)
file_name = 'demo_unified_context.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
