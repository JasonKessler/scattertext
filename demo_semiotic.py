from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import scattertext as st

newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))

vectorizer = TfidfVectorizer()
tfidf_X = vectorizer.fit_transform(newsgroups_train.data)

corpus = st.CorpusFromScikit(
	X=CountVectorizer(vocabulary=vectorizer.vocabulary_).fit_transform(newsgroups_train.data),
	y=newsgroups_train.target,
	feature_vocabulary=vectorizer.vocabulary_,
	category_names=newsgroups_train.target_names,
	raw_texts=newsgroups_train.data
).build()

semiotic_square = st.SemioticSquare(
	corpus,
	category_a='alt.atheism',
	category_b='soc.religion.christian',
	neutral_categories=['talk.religion.misc']
)

html = st.SemioticSquareViz(semiotic_square).get_html(num_terms=5)

fn = 'demo_semiotic_square_atheism_christianity.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ' + fn + ' in Chrome or Firefox.')
