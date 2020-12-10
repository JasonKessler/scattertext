import scattertext as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse.linalg import svds

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df['text'].apply(st.whitespace_nlp_with_sentences)
corpus = (st.CorpusFromParsedDocuments(convention_df,
                                       category_col='party',
                                       parsed_col='parse')
          .build()
          .get_stoplisted_unigram_corpus()
          .remove_infrequent_words(minimum_term_count=3, term_ranker=st.OncePerDocFrequencyRanker))
embeddings = TfidfTransformer().fit_transform(corpus.get_term_doc_mat()).T
U, S, VT = svds(embeddings, k = 3, maxiter=20000, which='LM')

x_dim = 0; y_dim = 1
projection = pd.DataFrame({'term':corpus.get_terms(),
                           'x':U.T[x_dim],
                           'y':U.T[y_dim]}).set_index('term')

html = st.produce_pca_explorer(corpus,
                               category='democrat',
                               category_name='Democratic',
                               not_category_name='Republican',
                               projection=projection,   
                               metadata=convention_df['speaker'],
                               width_in_pixels=1000,
                               x_dim=x_dim,
                               y_dim=y_dim,
                               show_axes_and_cross_hairs=True,
                               y_axis_values=[projection['y'].min(), 0, projection['y'].max()],
                               x_axis_values=[projection['x'].min(), 0, projection['x'].max()],
                               x_axis_values_format='.1f')
file_name = 'demo_axis_crossbars_and_labels.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open', file_name, 'in chrome')
