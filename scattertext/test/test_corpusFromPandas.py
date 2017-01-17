from unittest import TestCase

import numpy as np
import pandas as pd

from scattertext import chinese_nlp
from scattertext import whitespace_nlp
from scattertext.Corpus import Corpus
from scattertext.CorpusFromPandas import CorpusFromPandas


def get_docs_categories():
	documents = [u"What art thou that usurp'st this time of night,",
	             u'Together with that fair and warlike form',
	             u'In which the majesty of buried Denmark',
	             u'Did sometimes march? by heaven I charge thee, speak!',
	             u'Halt! Who goes there?',
	             u'[Intro]',
	             u'It is I sire Tone from Brooklyn.',
	             u'Well, speak up man what is it?',
	             u'News from the East sire! THE BEST OF BOTH WORLDS HAS RETURNED!',
	             u'Speak up, speak up, this is a repeat bigram.'
	             ]
	categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5 + ['???']
	return categories, documents


class TestCorpusFromPandas(TestCase):
	def test_term_doc(self):
		self.assertIsInstance(self.corpus, Corpus)
		self.assertEqual(set(self.corpus.get_categories()),
		                 set(['hamlet', 'jay-z/r. kelly', '???']))
		self.assertEqual(self.corpus.get_num_docs(), 10)
		term_doc_df = self.corpus.get_term_freq_df()
		self.assertEqual(term_doc_df.ix['of'].sum(), 3)

	def test_chinese_error(self):
		with self.assertRaises(Exception):
			CorpusFromPandas(self.df,
			                 'category',
			                 'text',
			                 nlp=chinese_nlp).build()

	def test_get_texts(self):
		self.assertTrue(all(self.df['text'] == self.corpus.get_texts()))

	def test_search(self):
		expected = pd.DataFrame({'text': ["What art thou that usurp'st this time of night,",
		                                  "Together with that fair and warlike form"],
		                         'category': ['hamlet', 'hamlet']})
		self.assertIsInstance(self.corpus, Corpus)
		returned = self.corpus.search('that')
		np.testing.assert_array_equal(expected, returned)

	def test_search_bigram(self):
		expected = pd.DataFrame({'text': [u'Well, speak up man what is it?',
		                                  u'Speak up, speak up, this is a repeat bigram.'],
		                         'category': ['jay-z/r. kelly', '???']})
		self.assertIsInstance(self.corpus, Corpus)
		returned = self.corpus.search('speak up')
		np.testing.assert_array_equal(expected, returned)

	def test_search_index(self):
		expected = np.array([7, 9])
		self.assertIsInstance(self.corpus, Corpus)
		returned = self.corpus.search_index('speak up')
		np.testing.assert_array_equal(expected, returned)

	@classmethod
	def setUp(cls):
		categories, documents = get_docs_categories()
		cls.df = pd.DataFrame({'category': categories,
		                       'text': documents})
		cls.corpus = CorpusFromPandas(cls.df,
		                              'category',
		                              'text',
		                              nlp=whitespace_nlp).build()
