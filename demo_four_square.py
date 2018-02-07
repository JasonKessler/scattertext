import time

import pandas as pd
import spacy

import scattertext as st

nlp = spacy.load('en', parser=False)
t0 = time.time()
print('reading dataset')
reviews_df = pd.read_csv('../jasonkessler.github.io/iclr2018_reviews.csv.bz2')
print('parsing', time.time() - t0, 's')
reviews_df['parse'] = reviews_df['review'].apply(st.whitespace_nlp_with_sentences)
print('building full corpus', time.time() - t0, 's')
full_corpus = (st.CorpusFromParsedDocuments(reviews_df,
                                            category_col='category',
                                            parsed_col='parse',
                                            feats_from_spacy_doc=st.PhraseMachinePhrases()
                                            ).build())
# print('building corpus', time.time() - t0, 's')
corpus = (full_corpus
          .keep_only_these_categories(['Accept, Positive',
                                       'Accept, Negative',
                                       'Reject, Positive',
                                       'Reject, Negative'],
                                      False))

print('compacting', time.time() - t0, 's')
term_ranker = st.OncePerDocFrequencyRanker
corpus = st.CompactTerms(corpus,
                         minimum_term_count=2,
                         term_ranker=term_ranker).compact()
print('finding priors', time.time() - t0, 's')
priors = (st.PriorFactory(full_corpus, starting_count=0.01)
          .use_all_categories()
          .get_priors())
print('building four square', time.time() - t0, 's')

four_square = st.FourSquare(
	corpus,
	category_a_list=['Accept, Positive'],
	not_category_a_list=['Reject, Negative'],
	category_b_list=['Accept, Negative'],
	not_category_b_list=['Reject, Positive'],
	term_ranker=term_ranker,
	scorer=st.LogOddsRatioInformativeDirichletPrior(priors, 10),
	labels={'a': 'Positive Reviews of Accepted Papers',
	        'b': 'Negative Reviews of Accepted Papers',
	        'not_a_and_not_b': 'Rejections',
	        'a_and_b': 'Acceptances',
	        'a_and_not_b': 'Positive Reviews',
	        'b_and_not_a': 'Negative Reviews',
	        'not_a': 'Negative Reviews of Rejected Papers',
	        'not_b': 'Positive Reviews of Rejected Papers',
	        }
)
print('making html', time.time() - t0, 's')
html = st.produce_four_square_explorer(four_square=four_square,
                                       x_label='Pos-Neg',
                                       y_label='Accept-Reject',
                                       num_terms_semiotic_square=5,
                                       minimum_term_frequency=0,
                                       pmi_threshold_coefficient=0,
                                       term_ranker=term_ranker,
                                       metadata=(corpus._df['category'] + ': '
                                                 + corpus._df.rating + ', '
                                                 + corpus._df['title']))
import pdb;pdb.set_trace()
fn = 'demo_four_square_phrase.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
print('done', time.time() - t0, 's')
