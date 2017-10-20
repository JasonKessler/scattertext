from unittest import TestCase

import pandas as pd

from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.representations.Word2VecFromParsedCorpus import GensimPhraseAdder
from scattertext.test.test_corpusFromPandas import get_docs_categories


class TestGensimPhraseAdder(TestCase):
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

	def test_add_phrase(self):
		adder = GensimPhraseAdder()
		# to do
		#res = adder.add_phrases(self.corpus)

		# self.fail()
