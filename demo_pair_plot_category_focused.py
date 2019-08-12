from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA

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
).build().get_unigram_corpus()

html = st.produce_category_focused_pairplot(
    corpus=corpus,
    category_projector=st.CategoryProjector(projector=PCA(10)),
    category='alt.atheism'
)

file_name = 'demo_pair_plot_category_focused.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
