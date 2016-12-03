from unittest import TestCase

import pandas as pd

from scattertext import fast_but_crap_nlp, CorpusFromParsedDocuments, ParsedCorpus
from scattertext.test.test_TermDocMat import get_hamlet_docs, get_hamlet_snippet_binary_category
from scattertext.test.test_corpusFromPandas import get_docs_categories
from scipy.sparse import bsr_matrix

class TestCorpusFromParsedDocuments(TestCase):
	@classmethod
	def setUp(cls):
		cls.categories, cls.documents = get_docs_categories()
		cls.parsed_docs = []
		for doc in cls.documents:
			cls.parsed_docs.append(fast_but_crap_nlp(doc))
		cls.df = pd.DataFrame({'category': cls.categories,
		                       'parsed': cls.parsed_docs})
		cls.corpus_fact = CorpusFromParsedDocuments(cls.df, 'category', 'parsed')

	def test_get_y_and_populate_category_idx_store(self):
		self.corpus_fact.build()
		self.assertEqual([0, 0, 0, 0, 1, 1, 1, 1, 1, 2], list(self.corpus_fact.y))
		self.assertEqual([(0, 'hamlet'), (1, 'jay-z/r. kelly'), (2, '???')],
		                 list(sorted(list(self.corpus_fact._category_idx_store.items()))))

	def test_get_term_idx_and_x(self):
		docs = [fast_but_crap_nlp('aa aa bb.'),
		 fast_but_crap_nlp('bb aa a.')]
		df = pd.DataFrame({'category': ['a', 'b'],
		                   'parsed': docs})
		corpus_fact = CorpusFromParsedDocuments(df, 'category', 'parsed')
		corpus = corpus_fact.build()
		self.assertEqual(list(corpus_fact._term_idx_store.items()),
		                 [(0, 'aa'), (1, 'aa aa'), (2, 'bb'), (3, 'aa bb'), (4, 'a'),
		                  (5, 'bb aa'), (6, 'aa a')]
		                 )
		self.assertEqual(list(sorted(corpus_fact.X.todok().items())),
		                 [((0, 0), 2), ((0, 1), 1), ((0, 2), 1), ((0, 3), 1),
		                  ((1, 0), 1), ((1, 2), 1), ((1, 4), 1), ((1, 5), 1), ((1, 6), 1)]
		                 )
		self.assertTrue(isinstance(corpus, ParsedCorpus))

	def test_hamlet(self):
		raw_docs = get_hamlet_docs()
		categories = [get_hamlet_snippet_binary_category(doc) for doc in raw_docs]
		docs = [fast_but_crap_nlp(doc) for doc in raw_docs]
		df = pd.DataFrame({'category': categories,
		                   'parsed': docs})
		corpus_fact = CorpusFromParsedDocuments(df, 'category', 'parsed')
		corpus = corpus_fact.build()
		tdf = corpus.get_term_freq_df()
		self.assertEqual(list(tdf.ix['play']), [37, 5])
		print(tdf.ix['play'])
		self.assertFalse(any(corpus.search('play').apply(lambda x: 'plfay' in str(x['parsed']), axis=1)))
		self.assertTrue(all(corpus.search('play').apply(lambda x: 'play' in str(x['parsed']), axis=1)))

		#!!! to do verify term doc matrix
		play_term_idx = corpus_fact._term_idx_store.getidx('play')
		play_X = corpus_fact.X.todok()[:, play_term_idx]

		self.assertEqual(play_X.sum(), 37 + 5)


