import io
from zipfile import ZipFile

import agefromname
import nltk
import pandas as pd
import urllib.request

import scattertext as st

nlp = st.tweet_tokenzier_factory(nltk.tokenize.TweetTokenizer())
with ZipFile(io.BytesIO(urllib.request.urlopen(
		'http://followthehashtag.com/content/uploads/USA-Geolocated-tweets-free-dataset-Followthehashtag.zip'
).read())) as zf:
	df = pd.read_excel(zf.open('dashboard_x_usa_x_filter_nativeretweets.xlsx'))
df['parse'] = df['Tweet content'].apply(nlp)

male_prob = agefromname.AgeFromName().get_all_name_male_prob()

df['first_name'] = df['User Name'].apply(lambda x: x.split()[0].lower() if type(x) == str and len(x.split()) > 0 else x)
df_aug = pd.merge(df, male_prob, left_on='first_name', right_index=True)
df_aug['gender'] = df_aug['prob'].apply(lambda x: 'm' if x > 0.9 else 'f' if x < 0.1 else '?')
df_mf = df_aug[df_aug['gender'].isin(['m', 'f'])]

corpus = st.CorpusFromParsedDocuments(df_mf,
                                      parsed_col='parse',
                                      category_col='gender',
                                      feats_from_spacy_doc=st.FeatsFromSpacyDocOnlyEmoji()
                                      ).build()

html = st.produce_scattertext_explorer(corpus,
                                       category='f',
                                       category_name='Female',
                                       not_category_name='Male',
                                       use_full_doc=True,
                                       metadata=df_mf['User Name'] + ' (@' + df_mf['Nickname'] + ') ' + df_mf[
	                                       'Date'].astype(str),
                                       show_characteristic=False,
                                       width_in_pixels=1000)
file_name = "EmojiGender.html"
open(file_name, 'wb').write(html.encode('utf-8'))
