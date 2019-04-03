from sklearn.decomposition import TruncatedSVD

import scattertext as st
from scattertext import ClassPercentageCompactor, CSRMatrixFactory
from scattertext.representations.CorpusSentenceIterator import CorpusSentenceIterator

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df['text'].apply(st.whitespace_nlp_with_sentences)

corpus = (st.CorpusFromParsedDocuments(convention_df,
                                       category_col='party',
                                       parsed_col='parse')
          .build()
          .get_stoplisted_unigram_corpus().select(ClassPercentageCompactor(term_count=3)))


html = st.produce_projection_explorer(corpus,
                                      embeddings=corpus.get_term_doc_mat(),
                                      projection_model=TruncatedSVD(n_components=30, n_iter=10),
                                      x_dim=0,
                                      y_dim=1,
                                      category='democrat',
                                      category_name='Democratic',
                                      not_category_name='Republican',
                                      metadata=convention_df.speaker,
                                      width_in_pixels=1000)
file_name = 'demo_bow_pca.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open', file_name, 'in chrome')
