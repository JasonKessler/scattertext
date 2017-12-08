from pprint import pprint
from unittest import TestCase

import pandas as pd

from scattertext import SemioticSquare
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.semioticsquare.SemioticSquare import EmptyNeutralCategoriesError


def get_docs_categories_semiotic():
	documents = [u"What art thou that usurp'st this time of night,",
	             u'Together with that fair and warlike form',
	             u'In which the majesty of buried Denmark',
	             u'Did sometimes march? by heaven I charge thee, speak!',
	             u'Halt! Who goes there?',
	             u'[Intro]',
	             u'It is I sire Tone from Brooklyn.',
	             u'Well, speak up man what is it?',
	             u'News from the East sire! THE BEST OF BOTH WORLDS HAS RETURNED!',
	             u'I think it therefore manifest, from what I have here advanced,',
	             u'that the main Point of Skill and Address, is to furnish Employment',
	             u'for this Redundancy of Vapour, and prudently to adjust the Season 1',
	             u'of it ; by which ,means it may certainly become of Cardinal'
	             ]
	categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5 + ['swift'] * 4
	return categories, documents

def get_test_semiotic_square():
	df = pd.DataFrame(data=pd.np.array(get_docs_categories_semiotic()).T,
	                  columns=['category', 'text'])
	corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
	semsq = SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', ['swift'])
	return semsq

class TestSemioticSquare(TestCase):
	def test_constructor(self):
		df = pd.DataFrame(data=pd.np.array(get_docs_categories_semiotic()).T,
		                  columns=['category', 'text'])
		corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
		SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', ['swift'])
		with self.assertRaises(AssertionError):
			SemioticSquare(corpus, 'XXXhamlet', 'jay-z/r. kelly', ['swift'])
		with self.assertRaises(AssertionError):
			SemioticSquare(corpus, 'hamlet', 'jay-z/r. kellyXXX', ['swift'])
		with self.assertRaises(AssertionError):
			SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', ['swift', 'asd'])
		with self.assertRaises(EmptyNeutralCategoriesError):
			SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', [])

	def test_lexicon_building(self):
		semsq = get_test_semiotic_square()
		self.assertEqual(semsq.category_a_, 'hamlet')
		self.assertEqual(semsq.category_b_, 'jay-z/r. kelly')
		self.assertEqual(semsq.neutral_categories_, ['swift'])
		self.assertNotEqual(semsq.category_a_words_, [])
		self.assertNotEqual(semsq.category_b_words_, [])
		self.assertNotEqual(semsq.not_category_a_and_b_words_, [])
		self.assertNotEqual(semsq.not_category_a_words_, [])
		self.assertNotEqual(semsq.not_category_b_words_, [])
		self.assertNotEqual(semsq.category_a_and_b_words_, [])
		self.assertNotEqual(semsq.category_a_vs_b_words_, [])
		self.assertNotEqual(semsq.category_b_vs_a_words_, [])

	def test_get_lexicons(self):
		semsq = get_test_semiotic_square()
		lexicons = semsq.get_lexicons()
		for category in self.categories():
			self.assertIn(category, lexicons)
			self.assertEqual(len(lexicons[category]), 10)

		lexicons = semsq.get_lexicons(num_terms=5)
		for category in self.categories():
			self.assertIn(category, lexicons)
			self.assertEqual(len(lexicons[category]), 5)

	def categories(self):
		return ['category_b_vs_a_words',
		        'category_b_words',
		        'not_category_a_words',
		        'not_category_a_and_b_words',
		        'category_a_vs_b_words',
		        'category_a_and_b_words',
		        'not_category_b_words',
		        'category_a_words']


