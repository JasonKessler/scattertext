from unittest import TestCase

import re

from scattertext import TermDocMatrixFactory


class Tok:
	def __init__(self, pos, lem, low):
		self.pos_ = pos
		self.lemma_ = lem
		self.lower_ = low

class Doc:
	def __init__(self,sents):
		self.sents = sents

def mock_nlp(doc):
	toks = []
	for tok in re.split(r"(\W)", doc):
		pos = 'WORD'
		if tok.strip() == '':
			pos = 'SPACE'
		elif re.match('\W', tok):
			pos = 'PUNCT'
		toks.append(Tok(pos, tok[:2], tok))
	return Doc([toks])

class TestTermDocMatrixFactory(TestCase):

	def test_build(self):
		documents = [u"What art thou that usurp'st this time of night,",
		             u'Together with that fair and warlike form',
		             u'In which the majesty of buried Denmark',
		             u'Did sometimes march? by heaven I charge thee, speak!',
		             u'Halt! Who goes there?',
		             u'[Intro]',
		             u'It is I sire Tone from Brooklyn.',
		             u'Well, speak up man what is it?',
		             u'News from the East sire! THE BEST OF BOTH WORLDS HAS RETURNED!'
		             ]
		categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5
		clean_function = lambda text: '' if text.startswith('[') else text
		term_doc_mat = TermDocMatrixFactory(
			category_text_iter=zip(categories, documents),
			clean_function=clean_function,
			nlp=mock_nlp
		).build()
		self.assertEqual(term_doc_mat.get_num_docs(), 8)
		self.assertEqual(term_doc_mat.get_categories(), ['hamlet', 'jay-z/r. kelly'])


