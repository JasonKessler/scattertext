import numpy as np
import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class BM25Difference(CorpusBasedTermScorer):
	'''
	Designed for use only in the term_scorer argument.
	This should really be inherit specific type.

	term_scorer = (BM25Difference(corpus, k1 = 1.4, b=0.9)
		.set_categories('Positive', ['Negative'], ['Plot']))

	html = st.produce_frequency_explorer(
		corpus,
		category='Positive',
		not_categories=['Negative'],
		neutral_categories=['Plot'],
		term_scorer=term_scorer,
		metadata=rdf['movie_name'],
		grey_threshold=0,
		show_neutral=True
	)
	file_name = 'output/rotten_fresh_bm25.html'
	open(file_name, 'wb').write(html.encode('utf-8'))
	IFrame(src=file_name, width=1300, height=700)
	'''

	def _set_scorer_args(self, **kwargs):
		self.k1 = kwargs.get('k1', 1.2)
		self.b = kwargs.get('b', 0.95)

	def get_scores(self, *args):
		'''
		In this case, args aren't used, since this information is taken
		directly from the corpus categories.

		Returns
		-------
		np.array, scores
		'''
		if self.tdf_ is None:
			raise Exception("Use set_category_name('category name', ['not category name', ...]) " +
			                "to set the category of interest")

		avgdl = self.tdf_.sum(axis=0).mean()

		def idf(cat):
			# Number of categories with term
			n_q = (self.tdf_ > 0).astype(int).max(axis=1).sum()
			N = len(self.tdf_)
			return (N - n_q + 0.5) / (n_q + 0.5)

		def length_adjusted_tf(cat):
			tf = self.tdf_[cat]
			dl = self.tdf_[cat].sum()
			return ((tf * (self.k1 + 1))
			        / (tf + self.k1 * (1 - self.b + self.b * (dl / avgdl))))

		def bm25_score(cat):
			return - length_adjusted_tf(cat) * np.log(idf(cat))

		scores = bm25_score('cat') - bm25_score('ncat')
		return scores

	def get_name(self):
		return 'BM25 difference'
