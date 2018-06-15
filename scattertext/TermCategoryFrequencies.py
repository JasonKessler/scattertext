import pkgutil
from io import StringIO

import pandas as pd

from scattertext.Common import DEFAULT_BACKGROUND_SCALER_ALGO, DEFAULT_BACKGROUND_BETA
from scattertext.termscoring import ScaledFScore


class TermCategoryFrequencies(object):
	'''
	This class allows you to produce scatter plots of raw term frequency counts.

	Occasionally, only term frequency statistics are available. This may happen in the case of very large,
	lost, or proprietary data sets. `TermCategoryFrequencies` is a corpus representation,that can accept this
	sort of data, along with any categorized documents that happen to be available.

	Let use the [Corpus of Contemporary American English](https://corpus.byu.edu/coca/) as an example.
	We'll construct a visualization
	to analyze the difference between spoken American English and English that occurs in fiction.

	```python
	convention_df = (pd.read_excel('https://www.wordfrequency.info/files/genres_sample.xls')
		      .dropna()
		      .set_index('lemma')[['SPOKEN', 'FICTION']]
		      .iloc[:1000])
	convention_df.head()
	          SPOKEN    FICTION
	lemma
	the    3859682.0  4092394.0
	I      1346545.0  1382716.0
	they   609735.0   352405.0
	she    212920.0   798208.0
	would  233766.0   229865.0
	```

	Transforming this into a visualization is extremely easy. Just pass a dataframe indexed on
	terms with columns indicating category-counts into the the `TermCategoryFrequencies` constructor.

	```python
	term_cat_freq = st.TermCategoryFrequencies(convention_df)
	```

	And call `produce_scattertext_explorer` normally:

	```python
	html = st.produce_scattertext_explorer(
		term_cat_freq,
		category='SPOKEN',
		category_name='Spoken',
		not_category_name='Fiction',
	)
	```


	[![demo_category_frequencies.html](https://jasonkessler.github.io/demo_category_frequencies.png)](https://jasonkessler.github.io/demo_category_frequencies.html)

	If you'd like to incorporate some documents into the visualization, you can add them into to the
	`TermCategoyFrequencies` object.

	First, let's extract some example Fiction and Spoken documents from the sample COCA corpus.

	```python
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
	```

	And we'll pass the `documents_df` dataframe into `TermCategoryFrequencies` via the `document_category_df`
	parameter.  Ensure the dataframe has two columns, 'text' and 'category'.  Afterward, we can
	call `produce_scattertext_explorer` (or your visualization function of choice) normally.

	```python
	doc_term_cat_freq = st.TermCategoryFrequencies(convention_df, document_category_df=document_df)

	html = st.produce_scattertext_explorer(
		doc_term_cat_freq,
		category='SPOKEN',
		category_name='Spoken',
		not_category_name='Fiction',
	)
	```
	'''

	def __init__(self,
	             category_frequency_df,
	             document_category_df=None,
	             unigram_frequency_path=None):
		'''
		Parameters
		----------
		category_frequency_df : pd.DataFrame
			Index is term, columns are categories, values are counts
		document_category_df : pd.DataFrame, optional
			Columns are text, category. Values are text (string) and category (string)
		unigram_frequency_path : See TermDocMatrix
		'''
		if document_category_df is not None:
			assert set(document_category_df.columns) == set(['text', 'category'])
		self._document_category_df = document_category_df
		self.term_category_freq_df = category_frequency_df
		self._unigram_frequency_path = unigram_frequency_path

	def get_num_terms(self):
		return len(self.term_category_freq_df)

	def get_categories(self):
		return list(self.term_category_freq_df.columns)

	def get_scaled_f_scores_vs_background(self,
	                                      scaler_algo=DEFAULT_BACKGROUND_SCALER_ALGO,
	                                      beta=DEFAULT_BACKGROUND_BETA):
		df = self.get_term_and_background_counts()
		df['Scaled f-score'] = ScaledFScore.get_scores_for_category(
			df['corpus'], df['background'], scaler_algo, beta
		)
		return df.sort_values(by='Scaled f-score', ascending=False)

	def get_term_and_background_counts(self):
		'''
		Returns
		-------
		A pd.DataFrame consisting of unigram term counts of words occurring
		 in the TermDocumentMatrix and their corresponding background corpus
		 counts.  The dataframe has two columns, corpus and background.

		>>> corpus.get_unigram_corpus.get_term_and_background_counts()
		                  corpus  background
		obama              702.0    565739.0
		romney             570.0    695398.0
		barack             248.0    227861.0
		...
		'''
		background_df = self._get_background_unigram_frequencies()
		corpus_freq_df = pd.DataFrame({'corpus': self.term_category_freq_df.sum(axis=1)})
		corpus_unigram_freq = corpus_freq_df.loc[[w for w in corpus_freq_df.index if ' ' not in w]]
		df = corpus_unigram_freq.join(background_df, how='outer').fillna(0)
		del df.index.name
		return df

	def _get_background_unigram_frequencies(self):
		if self._unigram_frequency_path:
			unigram_freq_table_buf = open(self._unigram_frequency_path)
		else:
			unigram_freq_table_buf = StringIO(pkgutil.get_data('scattertext', 'data/count_1w.txt')
			                                  .decode('utf-8'))
		to_ret = (pd.read_table(unigram_freq_table_buf,
		                        names=['word', 'background'])
		          .sort_values(ascending=False, by='background')
		          .drop_duplicates(['word'])
		          .set_index('word'))
		return to_ret

	def list_extra_features(self):
		raise Exception("Not implemented in TermCategoryFrequencies")

	def get_doc_indices(self):
		'''
		Returns
		-------
		np.array

		Integer document indices
		'''
		if self._document_category_df is None:
			return pd.np.array([])
		categories_d = {d: i for i, d in enumerate(self.get_categories())}
		return self._document_category_df.category.apply(categories_d.get).values

	def get_texts(self):
		'''
		Returns
		-------
		np.array

		Texts
		'''
		if self._document_category_df is None:
			return pd.np.array([])
		return self._document_category_df.text.values

	def get_term_category_frequencies(self, scatterchartdata):
		'''
		Parameters
		----------
		scatterchartdata : ScatterChartData

		Returns
		-------
		pd.DataFrame
		'''
		df = self.term_category_freq_df.rename(
			columns={c: c + ' freq' for c in self.term_category_freq_df}
		)
		df.index.name = 'term'
		return df

	def apply_ranker(self, term_ranker):
		'''
		Parameters
		----------
		term_ranker : TermRanker
			We'll ignore this

		Returns
		-------
		pd.Dataframe
		'''
		return self.get_term_category_frequencies(None)
