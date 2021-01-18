from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
import scattertext as st

newsgroups_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(newsgroups_train.data)

tdm = st.CorpusFromTermFrequencies(
    X=X,
    term_vocabulary=vectorizer.vocabulary_
).build()


corpus = st.CorpusFromTermFrequencies(
    X=X,
    term_vocabulary=vectorizer.vocabulary_,
    text_df=pd.DataFrame({'Text': newsgroups_train.data,
                          'Category': np.array(newsgroups_train.target_names)[newsgroups_train.target]}),
    text_col='Text',
    category_col='Category'
).build()

