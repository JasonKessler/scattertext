# currently in development

from collections import defaultdict
from time import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.utils import shuffle

import scattertext as st

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category \
	.apply(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])

corpus = st.CorpusFromPandas(
	movie_df,
	category_col='category',
	text_col='text',
	nlp=st.whitespace_nlp_with_sentences
).build().get_unigram_corpus()

term_scorer = (st.ZScores(corpus).set_categories('Positive', ['Negative'], ['Plot']))

scores = term_scorer.get_scores()
pos_neg_mask = np.isin(corpus.get_category_names_by_row(), ['Positive', 'Negative'])
X = corpus.get_term_doc_mat()[pos_neg_mask]
y = corpus.get_category_names_by_row()[pos_neg_mask]
y = y == 'Positive'
X = X.multiply(scores).tocsr()

clf = RandomForestClassifier(n_estimators=50)  # .fit(X, y)
# importances = clf.feature_importances_ * ((term_scorer.get_scores() > 0) * 2 - 1)

# import pdb; pdb.set_trace()
scores = defaultdict(list)
pred_diff = defaultdict(list)
n_feats = 100
kf = KFold(n_splits=2, shuffle=True)
n_iter = 0
t0 = time()
for train_idx, test_idx in kf.split(X):
	print(n_iter)
	X_train, X_test = X[train_idx], X[test_idx]
	Y_train, Y_test = y[train_idx], y[test_idx]
	print('fitting', time() - t0)
	r = clf.fit(X_train, Y_train)
	top_feats = np.argsort(-clf.feature_importances_)[:n_feats]
	print('fit', time() - t0)
	preds = clf.predict_proba(X_test).T[0]
	acc = accuracy_score(Y_test, clf.predict(X_test))
	print('acc', acc)
	X_test = X_test.tolil()
	for i, feati in enumerate(top_feats):
		if i % 100 == 0: print(i, n_feats, time() - t0)

		oldXfeat = X_test[:, feati]
		X_test[:, feati] = shuffle(X_test[:, feati])
		shuffle_preds = clf.predict_proba(X_test.tocsr()).T[0]
		pred_diff[corpus.get_terms()[feati]] = (preds - shuffle_preds).sum()
		shuff_acc = accuracy_score(Y_test, shuffle_preds > 0.5)
		X_test[:, feati] = oldXfeat
		scores[corpus.get_terms()[feati]].append((acc - shuff_acc) / acc)
print("Features sorted by their score:")
print(sorted([(round(np.mean(score), 4), feat) for
              feat, score in scores.items()], reverse=True))

print("Features sorted by their pred diff:")
print(sorted([(round(np.mean(score), 4), feat) for
              feat, score in pred_diff.items()], reverse=True))


term_scores = pd.Series(index=corpus.get_terms())
top_terms = pd.Series(scores).apply(np.mean)
term_scores.loc[top_terms.index] = top_terms.values
term_scores = term_scores.fillna(0)

html = st.produce_frequency_explorer(
	corpus,
	category='Positive',
	not_categories=['Negative'],
	neutral_categories=['Plot'],
	scores=term_scores.values,
	metadata=movie_df['movie_name'],
	grey_threshold=0,
	show_neutral=True
)

file_name = 'demo_rf.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
