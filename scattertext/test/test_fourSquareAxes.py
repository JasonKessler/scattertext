from unittest import TestCase

import pandas as pd

from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.semioticsquare.FourSquareAxis import FourSquareAxes


def get_docs_categories_four():
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
	             u'of it ; by which ,means it may certainly become of Cardinal',
	             u"Ain't it just like the night to play tricks when you're tryin' to be so quiet?",
	             u"We sit here stranded, though we're all doin' our best to deny it",
	             u"And Louise holds a handful of rain, temptin' you to defy it",
	             u'Lights flicker from the opposite loft',
	             u'In this room the heat pipes just cough',
	             u'The country music station plays soft']
	categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5 + ['swift'] * 4 + ['dylan'] * 6
	return categories, documents


class TestFourSquareAxes(TestCase):
	def test_build(self):
		corpus = self._get_test_corpus()
		with self.assertRaises(AssertionError):
			fs = FourSquareAxes(corpus, 'hamlet', ['jay-z/r. kelly'], ['swift'], ['dylan'])
		with self.assertRaises(AssertionError):
			fs = FourSquareAxes(corpus, ['hamlet'], 'jay-z/r. kelly', ['swift'], ['dylan'])
		with self.assertRaises(AssertionError):
			fs = FourSquareAxes(corpus, ['hamlet'], ['jay-z/r. kelly'], 'swift', ['dylan'])
		with self.assertRaises(AssertionError):
			fs = FourSquareAxes(corpus, ['hamlet'], ['jay-z/r. kelly'], ['swift'], 'dylan')
		fs = FourSquareAxes(corpus, ['hamlet'], ['jay-z/r. kelly'], ['swift'], ['dylan'])
		self.assertEqual(fs.get_labels(),
		                 {'a_and_b_label': 'swift',
		                  'a_and_not_b_label': 'hamlet',
		                  'a_label': '',
		                  'b_and_not_a_label': 'jay-z/r. kelly',
		                  'b_label': '',
		                  'not_a_and_not_b_label': 'dylan',
		                  'not_a_label': '',
		                  'not_b_label': ''})
		fs = FourSquareAxes(corpus, ['hamlet'], ['jay-z/r. kelly'], ['swift'], ['dylan'],
		                    labels={'a': 'swiftham', 'b': 'swiftj'})
		self.assertEqual(fs.get_labels(),
		                 {'a_and_b_label': 'swift',
		                  'a_and_not_b_label': 'hamlet',
		                  'a_label': 'swiftham',
		                  'b_and_not_a_label': 'jay-z/r. kelly',
		                  'b_label': 'swiftj',
		                  'not_a_and_not_b_label': 'dylan',
		                  'not_a_label': '',
		                  'not_b_label': ''})
		axes = fs.get_axes()
		self.assertEqual(len(axes), len(corpus.get_terms()))
		self.assertEqual(set(axes.columns), {'x', 'y', 'counts'})
		fs.lexicons

	def _get_test_corpus(self):
		cats, docs = get_docs_categories_four()
		df = pd.DataFrame({'category': cats, 'text': docs})
		corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
		return corpus

	def _get_test_semiotic_square(self):
		corpus = self._get_test_corpus()
		semsq = FourSquareAxes(corpus, ['hamlet'], ['jay-z/r. kelly'], ['swift'], ['dylan'])
		return semsq
