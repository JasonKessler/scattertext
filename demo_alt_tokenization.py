import scattertext as st
import pandas as pd
import re


data = [
	{'text': "I don't think you'll want to.", 'category': 'a'},
	{'text': "You'll have a didn't a-b #dfs .", 'category': 'a'},
	{'text': "You'll shoudn't #have a, didn't a-b #dfs .", 'category': 'a'},
	{'text': "Can't not get along to didn't.", 'category': 'b'},
	{'text': "Can't try aba-ba alo33ng to didn't.", 'category': 'b'},
	{'text': "Can't no't g'e't al33ong 3to5.", 'category': 'b'},
	{'text': "You haven't changed a b'it.", 'category': 'c'},
	{'text': "You haven't changed a b'it.", 'category': 'c'},
	{'text': "You haven't ch5ng3d a bit.", 'category': 'c'}
]

df = pd.DataFrame(data)
df['parse'] = df.text.apply(lambda x: st.whitespace_nlp_with_sentences(x, tok_splitter_re=re.compile('( )')))
corpus = st.CorpusFromParsedDocuments(df, parsed_col='parse', category_col='category').build().get_unigram_corpus()

semiotic_square = st.SemioticSquare(
	corpus,
	category_a='a',
	category_b='b',
	neutral_categories=['c'],
	scorer=st.RankDifference(),
	labels={'not_a_and_not_b': 'Plot Descriptions',
	        'a_and_b': 'Reviews',
	        'a_and_not_b': 'Positive',
	        'b_and_not_a': 'Negative',
	        'a':'',
	        'b':'',
	        'not_a':'',
	        'not_b':''}
)

html = st.produce_semiotic_square_explorer(semiotic_square,
                                           category_name='a',
                                           not_category_name='b',
                                           x_label='Fresh-Rotten',
                                           y_label='Plot-Review',
                                           num_terms_semiotic_square=20,
										   minimum_term_frequency=0,
										   pmi_filter_thresold=0,
                                           neutral_category_name='Plot Description')

fn = 'demo_alt_tokenization.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
