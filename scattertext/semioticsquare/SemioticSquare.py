from scipy.stats import hmean

from scattertext.termscoring import ScaledFScore


class EmptyNeutralCategoriesError(Exception): pass


class SemioticSquare(object):
	'''
	Create a visualization of a semiotic square.  Requires Corpus to have
	at least three categories.
	>>> newsgroups_train = fetch_20newsgroups(subset='train',
	...   remove=('headers', 'footers', 'quotes'))
	>>> vectorizer = CountVectorizer()
	>>> X = vectorizer.fit_transform(newsgroups_train.data)
	>>> corpus = st.CorpusFromScikit(
	... 	X=X,
	... 	y=newsgroups_train.target,
	... 	feature_vocabulary=vectorizer.vocabulary_,
	... 	category_names=newsgroups_train.target_names,
	... 	raw_texts=newsgroups_train.data
	... 	).build()
	>>> semseq = SemioticSquare(corpus,
	... 	category_a = 'alt.atheism',
	... 	category_b = 'soc.religion.christian',
	... 	neutral_categories = ['talk.religion.misc']
	... )
	>>> html = SemioticSquareViz(semseq).to_html()
	'''

	def __init__(self,
	             term_doc_matrix, category_a, category_b, neutral_categories,
	             scorer=None):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			TermDocMatrix (or descendant) which will be used in constructing square.
		category_a : str
			Category name for term A
		category_b : str
			Category name for term B (in opposition to A)
		neutral_categories : list[str]
			List of category names that A and B will be contrasted to.  Should be in same domain.
		scorer : termscoring class, optional
			Term scoring class for lexicon mining
		'''
		self.term_doc_matrix_ = term_doc_matrix
		assert category_a in term_doc_matrix.get_categories()
		assert category_b in term_doc_matrix.get_categories()
		for category in neutral_categories:
			assert category in term_doc_matrix.get_categories()
		if len(neutral_categories) == 0:
			raise EmptyNeutralCategoriesError()
		self.category_a_ = category_a
		self.category_b_ = category_b
		self.neutral_categories_ = neutral_categories
		self.scorer = ScaledFScore if scorer is None else scorer
		self._build_lexicons()

	def get_lexicons(self, num_terms=10):
		'''
		Parameters
		----------
		num_terms : int, default 10
			Number of terms to return in each lexicon

		Returns
		-------
			dict
			 Contains the following keys, with values
			 as lists of num_terms strings
			 - category_a_words
			 - category_b_words
			 - not_category_a_and_b_words
			 - not_category_a_words
			 - not_category_b_words
			 - category_a_and_b_words
			 - category_a_vs_b_words
			 - category_b_vs_a_words
		'''
		return {
			'category_a_words': self.category_a_words_[:num_terms],
			'category_b_words': self.category_b_words_[:num_terms],
			'not_category_a_and_b_words': self.not_category_a_and_b_words_[:num_terms],
			'not_category_a_words': self.not_category_a_words_[:num_terms],
			'not_category_b_words': self.not_category_b_words_[:num_terms],
			'category_a_and_b_words': self.category_a_and_b_words_[:num_terms],
			'category_a_vs_b_words': self.category_a_vs_b_words_[:num_terms],
			'category_b_vs_a_words': self.category_b_vs_a_words_[:num_terms]
		}

	def _build_lexicons(self):
		tdf = (self.term_doc_matrix_.get_term_doc_count_df()
		       [[t + ' freq' for t
		         in [self.category_a_, self.category_b_] + self.neutral_categories_]])
		tdf = tdf[tdf.sum(axis=1) > 0]
		self._find_a_vs_b_and_b_vs_a(tdf)
		tdf[self.category_a_ + ' scores'] = self.scorer.get_scores(
			tdf[self.category_a_ + ' freq'],
			tdf[[t for t in tdf.columns if t != self.category_a_ + ' freq']].sum(axis=1))
		tdf[self.category_b_ + ' scores'] = self.scorer.get_scores(
			tdf[self.category_b_ + ' freq'],
			tdf[[t for t in tdf.columns if t != self.category_b_ + ' freq']].sum(axis=1))
		tdf[self.category_a_ + ' + ' + self.category_b_ + ' scores'] = tdf[
			[t + ' scores' for t in [self.category_a_, self.category_b_]]].apply(
			lambda x: hmean(x) if min(x) > 0 else 0, axis=1)

		tdf["not " + self.category_a_ + ' scores'] = self.scorer.get_scores(
			tdf[[t for t in tdf.columns if t != self.category_a_ + ' freq']].sum(axis=1),
			tdf[self.category_a_ + ' freq'])
		tdf["not " + self.category_b_ + ' scores'] = self.scorer.get_scores(
			tdf[[t for t in tdf.columns if t != self.category_b_ + ' freq']].sum(axis=1),
			tdf[self.category_b_ + ' freq'])
		tdf["not " + self.category_a_ + ' + ' + self.category_b_ + ' scores'] = tdf[
			['not ' + t + ' scores' for t in [self.category_a_, self.category_b_]]].apply(
			lambda x: hmean(x) if min(x) > 0 else 0, axis=1)

		self.category_a_words_ = list(tdf.sort_values(by=self.category_a_ + ' scores',
		                                          ascending=False).index)
		self.category_b_words_ = list(tdf.sort_values(by=self.category_b_ + ' scores',
		                                          ascending=False).index)
		self.category_a_and_b_words_ = list(
			tdf.sort_values(by=self.category_a_ + ' + ' + self.category_b_ + ' scores',
			                ascending=False).index)
		self.not_category_a_words_ = list(
			tdf.sort_values(by='not ' + self.category_a_ + ' scores',
			                ascending=False).index)
		self.not_category_b_words_ = list(
			tdf.sort_values(by='not ' + self.category_b_ + ' scores',
			                ascending=False).index)
		self.not_category_a_and_b_words_ = list(
			tdf.sort_values(by='not ' + self.category_a_ + ' + ' + self.category_b_ + ' scores',
			                ascending=False).index)

	def _find_a_vs_b_and_b_vs_a(self, tdf):
		term_tdf = tdf[[self.category_a_ + ' freq', self.category_b_ + ' freq']]
		term_tdf = term_tdf[term_tdf.sum(axis=1) > 0]
		term_tdf[self.category_a_ + ' scores'] = self.scorer.get_scores(
			term_tdf[self.category_a_ + ' freq'],
			term_tdf[self.category_b_ + ' freq'])
		term_tdf[self.category_b_ + ' scores'] = self.scorer.get_scores(
			term_tdf[self.category_b_ + ' freq'],
			term_tdf[self.category_a_ + ' freq'])
		self.category_a_vs_b_words_ = list(term_tdf.sort_values(by=self.category_a_ + ' scores',
		                                                    ascending=False).index)
		self.category_b_vs_a_words_ = list(term_tdf.sort_values(by=self.category_b_ + ' scores',
		                                                    ascending=False).index)
