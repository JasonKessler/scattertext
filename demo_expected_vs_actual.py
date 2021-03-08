import numpy as np
import spacy
from sklearn.linear_model import LogisticRegression

from scattertext import SampleCorpora, produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas

nlp = spacy.load('en_core_web_sm')
convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=nlp).build()

term_freq_df = corpus.get_term_freq_df()

def scale(ar):
	return (ar - ar.min()) / (ar.max() - ar.min())

def zero_centered_scale(ar):
	ar[ar > 0] = scale(ar[ar > 0])
	ar[ar < 0] = -scale(-ar[ar < 0])
	return (ar + 1) / 2.


frequencies_scaled = scale(np.log(term_freq_df.sum(axis=1).values))
scores = corpus.get_logreg_coefs('democrat',
                                 LogisticRegression(penalty='l2', C=10, max_iter=10000, n_jobs=-1))
scores_scaled = zero_centered_scale(scores)

html = produce_scattertext_explorer(corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    minimum_term_frequency=5,
                                    width_in_pixels=1000,
                                    x_coords=frequencies_scaled,
                                    y_coords=scores_scaled,
                                    scores=scores,
                                    sort_by_dist=False,
                                    metadata=convention_df['speaker'],
                                    x_label='Log frequency',
                                    y_label='L2-penalized logistic regression coef')
fn = 'demo_expected_vs_actual.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % fn)
