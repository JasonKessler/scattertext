import json
from unittest import TestCase

import numpy as np
import pandas as pd

from scattertext import CorpusFromParsedDocuments
from scattertext import whitespace_nlp
from scattertext.DocsAndLabelsFromCorpus import DocsAndLabelsFromCorpus, \
	DocsAndLabelsFromCorpusSample
from scattertext.test.test_corpusFromPandas import get_docs_categories
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus_with_meta


class TestDocsAndLabelsFromCorpus(TestCase):
	@classmethod
	def setUp(cls):
		cls.categories, cls.documents = get_docs_categories()
		cls.parsed_docs = []
		for doc in cls.documents:
			cls.parsed_docs.append(whitespace_nlp(doc))
		cls.df = pd.DataFrame({'category': cls.categories,
		                       'parsed': cls.parsed_docs})
		cls.corpus = CorpusFromParsedDocuments(cls.df, 'category', 'parsed').build()

	def test_categories(self):
		for obj in [DocsAndLabelsFromCorpusSample(self.corpus, 1), DocsAndLabelsFromCorpus(self.corpus)]:
			output = obj.get_labels_and_texts()
			self.assertEqual(output['categories'], ['hamlet', 'jay-z/r. kelly', '???'])
			metadata = ['element 0 0', 'element 1 0', 'element 2 0', 'element 3 0',
			            'element 4 1', 'element 5 1', 'element 6 1',
			            'element 7 1', 'element 8 1', 'element 9 2']
			output = obj.get_labels_and_texts_and_meta(metadata)
			self.assertEqual(output['categories'], ['hamlet', 'jay-z/r. kelly', '???'])

	def test_main(self):
		d = DocsAndLabelsFromCorpus(self.corpus)
		output = d.get_labels_and_texts()
		self.assertTrue('texts' in output)
		self.assertTrue('labels' in output)
		self.assertEqual(self.corpus._y.astype(int).tolist(),
		                 output['labels'])
		self.assertEqual(self.corpus.get_texts().tolist(),
		                 output['texts'])

	def test_extra_features(self):
		corpus = build_hamlet_jz_corpus_with_meta()
		d = DocsAndLabelsFromCorpus(corpus).use_non_text_features()
		metadata = ['meta%s'%(i) for i in range(corpus.get_num_docs())]
		output = d.get_labels_and_texts_and_meta(metadata)
		extra_val = [{'cat3': 1, 'cat4': 2}, {'cat4': 2}, {'cat5': 1, 'cat3': 2},
		                                    {'cat9': 1, 'cat6': 2}, {'cat3': 1, 'cat4': 2},
		                                    {'cat1': 2, 'cat2': 1},
		                                    {'cat5': 1, 'cat2': 2},
		                                    {'cat3': 2, 'cat4': 1}]
		extra_val = [{'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}, {'cat1': 2}]

		self.assertEqual(output, {'categories': ['hamlet', 'jay-z/r. kelly'],
		                          'texts': ["what art thou that usurp'st this time of night,", 'together with that fair and warlike form', 'in which the majesty of buried denmark', 'did sometimes march? by heaven i charge thee, speak!', 'halt! who goes there?', 'it is i sire tone from brooklyn.', 'well, speak up man what is it?', 'news from the east sire! the best of both worlds has returned!'], 'meta': ['meta0', 'meta1', 'meta2', 'meta3', 'meta4', 'meta5', 'meta6', 'meta7'],
		                          'labels': [0, 0, 0, 0, 1, 1, 1, 1],
		                          'extra': extra_val}
)



	def test_metadata(self):
		d = DocsAndLabelsFromCorpus(self.corpus)
		metadata = ['element 0 0', 'element 1 0', 'element 2 0', 'element 3 0',
		            'element 4 1', 'element 5 1', 'element 6 1',
		            'element 7 1', 'element 8 1', 'element 9 2']
		output = d.get_labels_and_texts_and_meta(metadata)
		self.assertTrue('texts' in output)
		self.assertTrue('labels' in output)
		self.assertTrue('meta' in output)
		self.assertEqual(output['meta'], metadata)

	def test_max_per_category(self):
		docs_and_labels = DocsAndLabelsFromCorpusSample(self.corpus, max_per_category=2, seed=0)
		metadata = np.array(['element 0 0', 'element 1 0', 'element 2 0', 'element 3 0',
		                     'element 4 1', 'element 5 1', 'element 6 1',
		                     'element 7 1', 'element 8 1', 'element 9 2'])
		output = docs_and_labels.get_labels_and_texts_and_meta(metadata)
		self.assertTrue('texts' in output)
		self.assertTrue('labels' in output)
		self.assertTrue('meta' in output)
		self.assertTrue('extra' not in output)
		d = {}
		for text, lab, meta in zip(output['texts'], output['labels'], output['meta']):
			d.setdefault(lab, []).append(text)
		for lab, documents in d.items():
			self.assertLessEqual(len(documents), 2)
		json.dumps(d)

		docs_and_labels = DocsAndLabelsFromCorpusSample(self.corpus, max_per_category=2)
		output = docs_and_labels.get_labels_and_texts()
		self.assertTrue('texts' in output)
		self.assertTrue('labels' in output)
		self.assertTrue('meta' not in output)
		self.assertTrue('extra' not in output)
		d = {}
		for text, lab in zip(output['texts'], output['labels']):
			d.setdefault(lab, []).append(text)
		for lab, documents in d.items():
			self.assertLessEqual(len(documents), 2)
		json.dumps(d)


		docs_and_labels = DocsAndLabelsFromCorpusSample(self.corpus, max_per_category=2).use_non_text_features()
		output = docs_and_labels.get_labels_and_texts()
		self.assertTrue('texts' in output)
		self.assertTrue('labels' in output)
		self.assertTrue('meta' not in output)
		self.assertTrue('extra' in output)
		d = {}
		for text, lab in zip(output['texts'], output['labels']):
			d.setdefault(lab, []).append(text)
		for lab, documents in d.items():
			self.assertLessEqual(len(documents), 2)
		json.dumps(d)
