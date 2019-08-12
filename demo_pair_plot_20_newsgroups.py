from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import scattertext as st

import time

import scattertext.categoryprojector.pairplot

t0 = time.time()
newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
print(time.time() - t0)
vectorizer = TfidfVectorizer()
tfidf_X = vectorizer.fit_transform(newsgroups_train.data)

print(time.time() - t0)
corpus = st.CorpusFromScikit(
	X=CountVectorizer(vocabulary=vectorizer.vocabulary_).fit_transform(newsgroups_train.data),
	y=newsgroups_train.target,
	feature_vocabulary=vectorizer.vocabulary_,
	category_names=newsgroups_train.target_names,
	raw_texts=newsgroups_train.data
).build().get_unigram_corpus()
print(time.time() - t0)

html = scattertext.produce_pairplot(corpus)
print(time.time() - t0)
file_name = 'demo_pair_plot.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
print(time.time() - t0)
