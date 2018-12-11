import scattertext as st
import pandas as pd

fn = 'demo_multi_category_pca.html'
df = st.SampleCorpora.RottenTomatoes.get_data()
df['parse'] = df['text'].apply(st.whitespace_nlp_with_sentences)
corpus = (st.CorpusFromParsedDocuments(df, category_col='category', parsed_col='parse').build().get_unigram_corpus())

corpus, axes = st.EmbeddingsResolver(corpus).set_embeddings_model().project_embeddings()
#import pdb; pdb.set_trace()
#projection = pd.DataFrame({'term': corpus.get_terms(), 'x': axes.T[0], 'y': axes.T[1]}).set_index('term')

term_colors = st.CategoryColorAssigner(corpus).get_term_colors()
print(corpus.get_categories())
html = st.produce_pca_explorer(corpus,
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
                               color_func="(function(d) {return modelInfo.term_colors[d.term]})")
file_name = 'demo_multi_category_pca.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
