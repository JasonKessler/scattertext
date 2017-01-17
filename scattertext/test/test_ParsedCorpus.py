from unittest import TestCase

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from scattertext import whitespace_nlp, CorpusFromParsedDocuments
from scattertext.test.test_corpusFromPandas import get_docs_categories


class TestParsedCorpus(TestCase):
	@classmethod
	def setUp(cls):
		cls.categories, cls.documents = get_docs_categories()
		cls.parsed_docs = []
		for doc in cls.documents:
			cls.parsed_docs.append(whitespace_nlp(doc))
		cls.df = pd.DataFrame({'category': cls.categories,
		                       'author': ['a', 'a', 'c', 'c', 'c',
		                                  'c', 'd', 'd', 'e', 'e'],
		                       'parsed': cls.parsed_docs,
		                       'document_lengths': [len(doc) for doc in cls.documents]})
		cls.corpus = CorpusFromParsedDocuments(cls.df, 'category', 'parsed').build()

	def test_get_text(self):
		self.assertEqual(len([x for x in self.corpus.get_texts()]),
		                 len(self.documents))
		self.assertEqual([str(x) for x in self.corpus.get_texts()][0],
		                 "what art thou that usurp'st this time of night,")

	def test_search(self):
		self.assertEqual(len(self.corpus.search('bigram')), 1)
		df = self.corpus.search('bigram')
		d = dict(df.iloc[0])
		self.assertEqual(d['category'], '???')
		self.assertEqual(d['document_lengths'], 44)
		self.assertEqual(str(d['parsed']), 'speak up, speak up, this is a repeat bigram.')
		self.assertEqual(len(self.corpus.search('the')), 2)

	def test_term_group_freq_df(self):
		'''
		Returns
		-------
		return pd.DataFrame indexed on terms with columns giving how many attributes in df

		'''
		group_df = self.corpus.term_group_freq_df('author')
		self.assertEqual(set(group_df.index),
		                 set(self.corpus._term_idx_store.values()))
		self.assertEqual(dict(group_df.ix['of']), {'??? freq': 0, 'hamlet freq': 2, 'jay-z/r. kelly freq': 1})
		self.assertEqual(dict(group_df.ix['speak up']),
		                 {'??? freq': 1, 'hamlet freq': 0, 'jay-z/r. kelly freq': 1})
