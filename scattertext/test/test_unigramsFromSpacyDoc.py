from collections import Counter
from unittest import TestCase

from scattertext.features.UnigramsFromSpacyDoc import UnigramsFromSpacyDoc

from scattertext.WhitespaceNLP import whitespace_nlp


class TestUnigramsFromSpacyDoc(TestCase):
	def test_get_feats(self):
		doc = whitespace_nlp("A a bb cc.")
		term_freq = UnigramsFromSpacyDoc().get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'bb': 1, 'cc': 1}),
		                 term_freq)
