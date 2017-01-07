from collections import Counter
from unittest import TestCase

from scattertext import fast_but_crap_nlp
from scattertext.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class TestFeatsFromSpacyDoc(TestCase):
	def test_main(self):
		doc = fast_but_crap_nlp("A a bb cc.")
		term_freq = FeatsFromSpacyDoc().get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'bb': 1, 'a bb': 1, 'cc': 1, 'a a': 1, 'bb cc': 1}),
		                 term_freq)

	def test_lemmas(self):
		doc = fast_but_crap_nlp("A a bb ddddd.")
		term_freq = FeatsFromSpacyDoc(use_lemmas=True).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'bb': 1, 'a bb': 1, 'dd': 1, 'a a': 1, 'bb dd': 1}),
		                 term_freq)

	def test_empty(self):
		doc = fast_but_crap_nlp("")
		term_freq = FeatsFromSpacyDoc().get_feats(doc)
		self.assertEqual(Counter(), term_freq)


	def test_entity_types_to_censor_not_a_set(self):
		doc = fast_but_crap_nlp("A a bb cc.", {'bb':'A'})
		with self.assertRaises(AssertionError):
			FeatsFromSpacyDoc(entity_types_to_censor='A').get_feats(doc)

	def test_entity_censor(self):
		doc = fast_but_crap_nlp("A a bb cc.", {'bb': 'BAD'})
		term_freq = FeatsFromSpacyDoc(entity_types_to_censor=set(['BAD'])).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'a BAD': 1, 'BAD cc': 1, 'cc': 1, 'a a': 1, 'BAD': 1}),
		                 term_freq)

	def test_entity_tags(self):
		doc = fast_but_crap_nlp("A a bb cc Bob.", {'bb': 'BAD'}, {'Bob': 'NNP'})
		term_freq = FeatsFromSpacyDoc(entity_types_to_censor=set(['BAD'])).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'a BAD': 1,
		                          'BAD cc': 1, 'cc': 1,
		                          'a a': 1, 'BAD': 1, 'bob': 1, 'cc bob': 1}),
		                 term_freq)
		term_freq = FeatsFromSpacyDoc(entity_types_to_censor=set(['BAD']),
		                              tag_types_to_censor=set(['NNP'])).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'a BAD': 1,
		                          'BAD cc': 1, 'cc': 1,
		                          'a a': 1, 'BAD': 1, 'NNP': 1, 'cc NNP': 1}),
		                 term_freq)
