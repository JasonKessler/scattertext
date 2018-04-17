import pandas as pd

import scattertext as st

'''
Sample genre frequencies from the Corpus of Contemporary American English via 
https://www.wordfrequency.info/100k_compare_to_60k_etc.asp .

We'll examine the difference between spoken and fiction, and just consider the top 1000
words in the sample.
'''
df = (pd.read_excel('https://www.wordfrequency.info/files/genres_sample.xls')
	      .dropna()
	      .set_index('lemma')[['SPOKEN', 'FICTION']]
	      .iloc[:1000])

term_cat_freq = st.TermCategoryFrequencies(df)

html = st.produce_scattertext_explorer(
	term_cat_freq,
	category='SPOKEN',
	category_name='Spoken',
	not_category_name='Fiction',
)

fn = 'demo_category_frequencies.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ./' + fn + ' in Chrome or Firefox.')

import requests, zipfile, io
coca_sample_url = 'http://corpus.byu.edu/cocatext/samples/text.zip'
zip_file = zipfile.ZipFile(io.BytesIO(requests.get(coca_sample_url).content))

document_df = pd.DataFrame(
	[{'text': zip_file.open(fn).read().decode('utf-8'),
	  'category': 'SPOKEN'}
	 for fn in zip_file.filelist if fn.filename.startswith('w_spok')][:2]
	+ [{'text': zip_file.open(fn).read().decode('utf-8'),
	    'category': 'FICTION'}
	   for fn in zip_file.filelist if fn.filename.startswith('w_fic')][:2])

doc_term_cat_freq = st.TermCategoryFrequencies(df, document_category_df=document_df)

html = st.produce_scattertext_explorer(
	doc_term_cat_freq,
	category='SPOKEN',
	category_name='Spoken',
	not_category_name='Fiction',
)

fn = 'demo_category_frequencies_sample_docs.html'
open(fn, 'wb').write(html.encode('utf-8'))
print('Open ./' + fn + ' in Chrome or Firefox.')

