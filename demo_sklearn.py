from lightning.classification import CDClassifier
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import f1_score
import scattertext as st

newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))

vectorizer = TfidfVectorizer()
tfidf_X = vectorizer.fit_transform(newsgroups_train.data)
clf = CDClassifier(penalty="l1/l2",
                   loss="squared_hinge",
                   multiclass=True,
                   max_iter=20,
                   alpha=1e-4,
                   C=1.0 / tfidf_X.shape[0],
                   tol=1e-3)
clf.fit(tfidf_X, newsgroups_train.target)

corpus = st.CorpusFromScikit(
	X=CountVectorizer(vocabulary=vectorizer.vocabulary_).fit_transform(newsgroups_train.data),
	y=newsgroups_train.target,
	feature_vocabulary=vectorizer.vocabulary_,
	category_names=newsgroups_train.target_names,
	raw_texts=newsgroups_train.data
).build()

html = st.produce_frequency_explorer(
	corpus,
	'alt.atheism',
	scores=clf.coef_[0],
	use_term_significance=False,
	terms_to_include=st.AutoTermSelector.get_selected_terms(corpus, clf.coef_[0]),
	metadata = ['/'.join(fn.split('/')[-2:]) for fn in newsgroups_train.filenames]
)

file_name = "demo_sklearn.html"
open(file_name, 'wb').write(html.encode('utf-8'))
print("open " + file_name)

sfs = (corpus.get_scaled_f_scores('alt.atheism') - 0.5) * 2
html = st.produce_frequency_explorer(
	corpus,
	'alt.atheism',
	scores=sfs,
	use_term_significance=False,
	terms_to_include=st.AutoTermSelector.get_selected_terms(corpus, sfs),
	metadata = ['/'.join(fn.split('/')[-2:]) for fn in newsgroups_train.filenames]
)

file_name = "demo_sklearn_sfs.html"
open(file_name, 'wb').write(html.encode('utf-8'))
print("open " + file_name)

sfs = (corpus.get_scaled_f_scores('alt.atheism', beta=1) - 0.5) * 2
html = st.produce_frequency_explorer(
	corpus,
	'alt.atheism',
	scores=sfs,
	use_term_significance=False,
	terms_to_include=st.AutoTermSelector.get_selected_terms(corpus, sfs),
	metadata = ['/'.join(fn.split('/')[-2:]) for fn in newsgroups_train.filenames]
)

file_name = "demo_sklearn_sfs_beta1.html"
open(file_name, 'wb').write(html.encode('utf-8'))
print("open " + file_name)


newsgroups_test = fetch_20newsgroups(subset='test',
                                     remove=('headers', 'footers', 'quotes'))
X_test = vectorizer.transform(newsgroups_test.data)
pred = clf.predict(X_test)
f1 = f1_score(pred, newsgroups_test.target, average='micro')
print("Microaveraged F1 score", f1)

