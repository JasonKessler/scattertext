import spacy
from sklearn.linear_model import Lasso
from sklearn.linear_model import LogisticRegression

from scattertext import SampleCorpora, sparse_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas

nlp = spacy.en.English()
convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=nlp).build()
scores = corpus.get_logreg_coefs('democrat',
                                 LogisticRegression(penalty='l1', C=10, max_iter=10000, n_jobs=-1))
html = sparse_explorer(corpus,
                       category='democrat',
                       category_name='Democratic',
                       not_category_name='Republican',
                       scores = scores,
                       minimum_term_frequency=5,
                       pmi_filter_thresold=4,
                       width_in_pixels=1000,
                       metadata=convention_df['speaker'])
open('./demo_sparse.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_sparse.html in Chrome or Firefox.')
