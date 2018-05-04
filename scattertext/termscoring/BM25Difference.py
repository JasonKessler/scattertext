import pandas as pd
import numpy as np

class BM25Difference(object):
	'''
	Designed for use only in the term_scorer argument.
	This should really be inherit specific type.

	html = st.produce_frequency_explorer(
		corpus,
		category='Positive',
		not_categories=['Negative'],
		neutral_categories=['Plot'],
		term_scorer=BM25(corpus).set_categories('Positive', ['Negative'], ['Plot']),
		metadata=rdf['movie_name'],
		grey_threshold=0,
		show_neutral=True
	)
	file_name = 'output/rotten_fresh_bm25.html'
	open(file_name, 'wb').write(html.encode('utf-8'))
	IFrame(src=file_name, width=1300, height=700)
	'''
	def __init__(self, corpus, k1=1.2, b=0.95):
		self.k1 = k1
		self.b = b
		self.corpus = corpus
		self.category_names = corpus.get_categories()
		self.category_ids = corpus._y
		self.tdf = None

	def set_categories(self, category_name,
	                   not_category_names=[],
	                   neutral_category_names=[]):
		'''
		Specify the category to score. Optionally, score against a specific set of categories.
		'''
		tdf = self.corpus.get_term_freq_df()
		d = {'cat': tdf[category_name + ' freq']}
		if not_category_names == []:
			not_category_names = [c + ' freq' for c in self.corpus.get_categories()
			                      if c != category_name]
		else:
			not_category_names = [c + ' freq' for c in not_category_names]
		d['ncat'] = tdf[not_category_names].sum(axis=1)
		if neutral_category_names == []:
			neutral_category_names = [c + ' freq' for c in self.corpus.get_categories()
			                          if c != category_name and c not in not_category_names]
		else:
			neutral_category_names = [c + ' freq' for c in neutral_category_names]
		for i, c in enumerate(neutral_category_names):
			d['neut%s' % (i)] = tdf[c]
		self.tdf = pd.DataFrame(d)
		return self

	def get_scores(self, a, b):
		'''
		In this case, parameters a and b aren't used, since this information is taken
		directly from the corpus categories.

		Parameters
		----------
		a
		b

		Returns
		-------

		'''
		if self.tdf is None:
			raise Exception("Use set_category_name('category name', ['not category name', ...]) " +
			                "to set the category of interest")

		avgdl = self.tdf.sum(axis=0).mean()

		def idf(cat):
			# Number of categories with term
			n_q = (self.tdf > 0).astype(int).max(axis=1).sum()
			N = len(self.tdf)
			return (N - n_q + 0.5) / (n_q + 0.5)

		def length_adjusted_tf(cat):
			tf = self.tdf[cat]
			dl = self.tdf[cat].sum()
			return ((tf * (self.k1 + 1))
			        / (tf + self.k1 * (1 - self.b + self.b * (dl / avgdl))))

		def bm25_score(cat):
			return length_adjusted_tf(cat) * np.log(idf(cat))

		scores = bm25_score('cat') - bm25_score('ncat')
		return scores

	def get_name(self):
		return 'BM25 difference'
