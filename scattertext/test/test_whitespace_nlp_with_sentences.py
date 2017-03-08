from unittest import TestCase

from scattertext.WhitespaceNLP import whitespace_nlp_with_sentences


class TestWhitespace_nlp_with_sentences(TestCase):
	def test_whitespace_nlp_with_sentences(self):
		raw = '''Hi! My name
		is Jason.  You can call me
		Mr. J.  Is that your name too?
		Ha. Ha ha.
		'''
		self.assertEqual(whitespace_nlp_with_sentences(raw).text, raw)
		self.assertEqual(len(whitespace_nlp_with_sentences(raw).sents), 7)