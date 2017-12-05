from unittest import TestCase

from scattertext.WhitespaceNLP import whitespace_nlp_with_sentences, whitespace_nlp, Tok, Doc


class TestWhitespaceNLP(TestCase):
	def test_whitespace_nlp(self):
		raw = '''Hi! My name
		is Jason.  You can call me
		Mr. J.  Is that your name too?
		Ha. Ha ha.
		'''
		doc = whitespace_nlp(raw)
		self.assertEqual(len(list(doc)), 55)
		self.assertEqual(len(doc.sents), 1)
		tok = Tok('WORD', 'Jason', 'jason', 'Name', 'NNP')
		self.assertEqual(len(tok), 5)
		self.assertEqual(str(tok), 'jason')
		self.assertEqual(str(Doc([[Tok('WORD', 'Jason', 'jason', 'Name', 'NNP'),
		                           Tok('WORD', 'a', 'a', 'Name', 'NNP')]],
		                         raw='asdfbasdfasd')),
		                 'asdfbasdfasd')
		self.assertEqual(str(Doc([[Tok('WORD', 'Blah', 'blah', 'Name', 'NNP'),
		                           Tok('Space', ' ', ' ', ' ', ' '),
		                           Tok('WORD', 'a', 'a', 'Name', 'NNP')]])),
		                 'blah a')

	def test_whitespace_nlp_with_sentences(self):
		raw = '''Hi! My name
		is Jason.  You can call me
		Mr. J.  Is that your name too?
		Ha. Ha ha.
		'''
		self.assertEqual(whitespace_nlp_with_sentences(raw).text, raw)
		self.assertEqual(len(whitespace_nlp_with_sentences(raw).sents), 7)

	def test_whitespace_nlp_with_sentences_singleton(self):
		raw = 'Blah'
		self.assertEqual(whitespace_nlp_with_sentences(raw).text, raw)
		self.assertEqual(len(whitespace_nlp_with_sentences(raw).sents), 1)
		self.assertEqual(len(whitespace_nlp_with_sentences(raw).sents[0]), 1)

		raw = 'Blah.'
		self.assertEqual(whitespace_nlp_with_sentences(raw).text, raw)
		self.assertEqual(len(whitespace_nlp_with_sentences(raw).sents), 1)
		self.assertEqual(len(whitespace_nlp_with_sentences(raw).sents[0]), 2)
