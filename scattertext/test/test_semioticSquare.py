from unittest import TestCase

import pandas as pd
import numpy as np

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


def get_test_corpus():
	df = pd.DataFrame(data=np.array(get_docs_categories_semiotic()).T,
	                  columns=['category', 'text'])
	corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
	return corpus


def get_test_semiotic_square():
	corpus = get_test_corpus()
	semsq = SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', ['swift'])
	return semsq


class TestSemioticSquare(TestCase):
	def test_constructor(self):
		df = pd.DataFrame(data=np.array(get_docs_categories_semiotic()).T,
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

	def test_get_labels(self):
		corpus = get_test_corpus()
		semsq = SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', ['swift'])
		a, b = 'hamlet', 'jay-z/r. kelly'
		default_labels = {'a': a,
		                  'not_a': 'Not ' + a,
		                  'b': b,
		                  'not_b': 'Not ' + b,
		                  'a_and_b': a + ' + ' + b,
		                  'not_a_and_not_b': 'Not ' + a + ' + Not ' + b,
		                  'a_and_not_b': a + ' + Not ' + b,
		                  'b_and_not_a': 'Not ' + a + ' + ' + b}
		labels = semsq.get_labels()
		for name,default_label in default_labels.items():
			self.assertTrue(name + '_label' in labels)
			self.assertEqual(labels[name + '_label'], default_label)

		semsq = SemioticSquare(corpus, 'hamlet', 'jay-z/r. kelly', ['swift'], labels={'a':'AAA'})
		labels = semsq.get_labels()
		for name,default_label in default_labels.items():
			if name == 'a':
				self.assertEqual(labels[name + '_label'], 'AAA')
			else:
				self.assertTrue(name + '_label' in labels)
				self.assertEqual(labels[name + '_label'], default_label)

	def test_get_lexicons(self):
		semsq = get_test_semiotic_square()
		lexicons = semsq.get_lexicons()
		for category in self.categories():
			self.assertIn(category, lexicons)
			self.assertLessEqual(len(lexicons[category]), 10)

		lexicons = semsq.get_lexicons(5)
		for category in self.categories():
			self.assertIn(category, lexicons)
			self.assertLessEqual(len(lexicons[category]), 5)

	def test_get_axes(self):
		semsq = get_test_semiotic_square()
		ax = semsq.get_axes()
		self.assertEqual(list(sorted(ax.index)),
		                 list(sorted(semsq.term_doc_matrix_.get_terms())))

	def categories(self):
		return ['a',
		        'b',
		        'not_a',
		        'not_b',
		        'a_and_not_b',
		        'b_and_not_a',
		        'a_and_b',
		        'not_a_and_not_b']
