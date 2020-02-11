import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
import umap
import scattertext as st
from scipy.sparse.linalg import svds

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df['text'].apply(st.whitespace_nlp_with_sentences)
corpus = (st.CorpusFromParsedDocuments(convention_df,
                                       category_col='party',
                                       parsed_col='parse')
          .build()
          .get_stoplisted_unigram_corpus())
corpus = corpus.add_doc_names_as_metadata(corpus.get_df()['speaker'])

embeddings = TfidfTransformer().fit_transform(corpus.get_term_doc_mat())
projection_raw = umap.UMAP(min_dist=0.5, metric='cosine').fit_transform(embeddings).T
projection = pd.DataFrame({'term': corpus.get_metadata(),
                           'x': projection_raw[0],
                           'y': projection_raw[1]}).set_index('term')

category = 'democrat'
scores = (corpus.get_category_ids() == corpus.get_categories().index(category)).astype(int)
html = st.produce_pca_explorer(corpus,
                               category=category,
                               category_name='Democratic',
                               not_category_name='Republican',
                               metadata=convention_df['speaker'],
                               width_in_pixels=1000,
                               use_non_text_features=True,
                               use_full_doc=True,
                               projection=projection,
                               scores=scores,
                               show_top_terms=False)
file_name = 'demo_umap_documents.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
