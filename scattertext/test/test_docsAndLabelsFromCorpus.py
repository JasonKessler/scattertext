import json
from unittest import TestCase
import pandas as pd

from scattertext import CorpusFromParsedDocuments
from scattertext import fast_but_crap_nlp
from scattertext.DocsAndLabelsFromCorpus import DocsAndLabelsFromCorpus
from scattertext.test.test_corpusFromPandas import get_docs_categories


class TestDocsAndLabelsFromCorpus(TestCase):
	@classmethod
	def setUp(cls):
		cls.categories, cls.documents = get_docs_categories()
		cls.parsed_docs = []
		for doc in cls.documents:
			cls.parsed_docs.append(fast_but_crap_nlp(doc))
		cls.df = pd.DataFrame({'category': cls.categories,
		                       'parsed': cls.parsed_docs})
		cls.corpus = CorpusFromParsedDocuments(cls.df, 'category', 'parsed').build()

	def test_main(self):
		d = DocsAndLabelsFromCorpus(self.corpus)
		output = d.get_labels_and_texts()
		print(output)
		self.assertTrue('texts' in output)
		self.assertTrue('labels' in output)
		self.assertEqual(self.corpus._y.astype(int).tolist(),
		                 output['labels'])
		self.assertEqual(self.corpus.get_texts().tolist(),
		                 output['texts'])
		json.dumps(output)
