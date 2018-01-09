from unittest import TestCase

import pandas as pd

from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.representations.Word2VecFromParsedCorpus import Word2VecFromParsedCorpus, \
	Word2VecFromParsedCorpusBigrams
from scattertext.test.test_corpusFromPandas import get_docs_categories


class TestWord2VecFromParsedCorpus(TestCase):
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

	def test_make(self):
		gensim_is_present_and_working = False
		try:
			from gensim.models import word2vec
			gensim_is_present_and_working = True
		except:
			pass
		if gensim_is_present_and_working:
			with self.assertRaises(Exception):
				Word2VecFromParsedCorpus(3)
			Word2VecFromParsedCorpus(self.corpus)
			Word2VecFromParsedCorpus(self.corpus, word2vec.Word2Vec())

	def test_train(self):
		gensim_is_present_and_working = False
		try:
			from gensim.models import word2vec
			gensim_is_present_and_working = True
		except:
			pass
		if gensim_is_present_and_working:
			Word2VecFromParsedCorpus(self.corpus).train()

	def test_bigrams(self):
		gensim_is_present_and_working = False
		try:
			from gensim.models import word2vec
			gensim_is_present_and_working = True
		except:
			pass
		if gensim_is_present_and_working:
			Word2VecFromParsedCorpusBigrams(self.corpus).train()
