import io
from zipfile import ZipFile

import agefromname
import nltk
import pandas as pd
import urllib.request

import scattertext as st
from scattertext.termranking import OncePerDocFrequencyRanker

try:
	print("Downloading tweet dataset")
	df_mf = pd.read_csv('emoji_data.csv')
except:
	print("Downloading tweet dataset")
	with ZipFile(io.BytesIO(urllib.request.urlopen(
			'http://followthehashtag.com/content/uploads/USA-Geolocated-tweets-free-dataset-Followthehashtag.zip'
	).read())) as zf:
		df = pd.read_excel(zf.open('dashboard_x_usa_x_filter_nativeretweets.xlsx'))
	df['first_name'] = df['User Name'].apply(
		lambda x: x.split()[0].lower() if type(x) == str and len(x.split()) > 0 else x)
	male_prob = agefromname.AgeFromName().get_all_name_male_prob()
	df_aug = pd.merge(df, male_prob, left_on='first_name', right_index=True)
	df_aug['gender'] = df_aug['prob'].apply(lambda x: 'm' if x > 0.9 else 'f' if x < 0.1 else '?')
	df_mf = df_aug[df_aug['gender'].isin(['m', 'f'])]
	df_mf.to_csv('emoji_data.csv', index=False)

nlp = st.tweet_tokenzier_factory(nltk.tokenize.TweetTokenizer())
df_mf['parse'] = df_mf['Tweet content'].apply(nlp)

corpus = st.CorpusFromParsedDocuments(
	df_mf,
	parsed_col='parse',
	category_col='gender',
	feats_from_spacy_doc=st.FeatsFromSpacyDocOnlyEmoji()
).build()

html = st.produce_scattertext_explorer(
	corpus,
	category='f',
	category_name='Female',
	not_category_name='Male',
	use_full_doc=True,
	term_ranker=OncePerDocFrequencyRanker,
	sort_by_dist=False,
	metadata=(df_mf['User Name']
	          + ' (@' + df_mf['Nickname'] + ') '
	          + df_mf['Date'].astype(str)),
	width_in_pixels=1000
)

print('writing EmojiGender.html')
open("EmojiGender.html", 'wb').write(html.encode('utf-8'))
