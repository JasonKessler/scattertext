import re
from collections import Counter
from unittest import TestCase

from scattertext import whitespace_nlp
from scattertext.WhitespaceNLP import Tok, Doc, _regex_parse_sentence, whitespace_nlp_with_sentences
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc
from scattertext.features.FeatsFromSpacyDocOnlyNounChunks import FeatsFromSpacyDocOnlyNounChunks


def bad_whitespace_nlp(doc):
	toks = []
	for tok in doc.split():
		pos = 'WORD'
		if tok.strip() == '':
			pos = 'SPACE'
		elif re.match('^\W+$', tok):
			pos = 'PUNCT'
		toks.append(Tok(pos,
		                tok[:2].lower(),
		                tok.lower(),
		                ent_type='',
		                tag=''))
	return Doc([toks])


class Span:
	def __init__(self, toks):
		self.text = ' '.join([t.lower_ for t in toks])
	def __str__(self):
		return self.text

def whitespace_nlp_with_fake_chunks(doc, entity_type=None, tag_type=None):
	toks = _regex_parse_sentence(doc, entity_type, tag_type)
	words = [t for t in toks if t.pos_ == 'WORD']
	if len(words) < 5:
		return Doc([toks])
	else:
		return Doc([toks], noun_chunks=[Span(words[:2]), Span(words[1:3])])


class TestFeatsFromSpacyDoc(TestCase):
	def test_main(self):
		doc = whitespace_nlp("A a bb cc.")
		term_freq = FeatsFromSpacyDoc().get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'bb': 1, 'a bb': 1, 'cc': 1, 'a a': 1, 'bb cc': 1}),
		                 term_freq)

	def test_singleton_with_sentences(self):
		doc = whitespace_nlp_with_sentences("Blah")
		term_freq = FeatsFromSpacyDoc().get_feats(doc)
		self.assertEqual(Counter({'blah': 1}),
		                 term_freq)

	def test_lemmas(self):
		doc = whitespace_nlp("A a bb ddddd.")
		term_freq = FeatsFromSpacyDoc(use_lemmas=True).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'bb': 1, 'a bb': 1, 'dd': 1, 'a a': 1, 'bb dd': 1}),
		                 term_freq)

	def test_feats_from_spacy_doc_only_chunks(self):
		doc = whitespace_nlp_with_fake_chunks('This is a fake noun chunk generating sentence.')
		term_freq = FeatsFromSpacyDocOnlyNounChunks().get_feats(doc)
		self.assertEqual(term_freq, Counter({'this is': 1, 'is a': 1}))

	def test_empty(self):
		doc = whitespace_nlp("")
		term_freq = FeatsFromSpacyDoc().get_feats(doc)
		self.assertEqual(Counter(), term_freq)

	def test_entity_types_to_censor_not_a_set(self):
		doc = whitespace_nlp("A a bb cc.", {'bb': 'A'})
		with self.assertRaises(AssertionError):
			FeatsFromSpacyDoc(entity_types_to_censor='A').get_feats(doc)

	def test_entity_censor(self):
		doc = whitespace_nlp("A a bb cc.", {'bb': 'BAD'})
		term_freq = FeatsFromSpacyDoc(entity_types_to_censor=set(['BAD'])).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'a _BAD': 1, '_BAD cc': 1, 'cc': 1, 'a a': 1, '_BAD': 1}),
		                 term_freq)

	def test_entity_tags(self):
		doc = whitespace_nlp("A a bb cc Bob.", {'bb': 'BAD'}, {'Bob': 'NNP'})
		term_freq = FeatsFromSpacyDoc(entity_types_to_censor=set(['BAD'])).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'a _BAD': 1,
		                          '_BAD cc': 1, 'cc': 1,
		                          'a a': 1, '_BAD': 1, 'bob': 1, 'cc bob': 1}),
		                 term_freq)
		term_freq = FeatsFromSpacyDoc(entity_types_to_censor=set(['BAD']),
		                              tag_types_to_censor=set(['NNP'])).get_feats(doc)
		self.assertEqual(Counter({'a': 2, 'a _BAD': 1,
		                          '_BAD cc': 1, 'cc': 1,
		                          'a a': 1, '_BAD': 1, 'NNP': 1, 'cc NNP': 1}),
		                 term_freq)

	def test_strip_final_period(self):
		doc = bad_whitespace_nlp('''I CAN'T ANSWER THAT
 QUESTION.
 I HAVE NOT ASKED THEM
 SPECIFICALLY IF THEY HAVE
 ENOUGH.''')
		feats = FeatsFromSpacyDoc().get_feats(doc)
		self.assertEqual(feats, Counter(
			{'i': 2, 'have': 2, 'that question.': 1, 'answer': 1, 'question.': 1, 'enough.': 1, 'i have': 1,
			 'them specifically': 1, 'have enough.': 1, 'not asked': 1, 'they have': 1, 'have not': 1, 'specifically': 1,
			 'answer that': 1, 'question. i': 1, "can't": 1, 'if': 1, 'they': 1, "can't answer": 1, 'asked': 1, 'them': 1,
			 'if they': 1, 'asked them': 1, 'that': 1, 'not': 1, "i can't": 1, 'specifically if': 1}))
		feats = FeatsFromSpacyDoc(strip_final_period=True).get_feats(doc)
		self.assertEqual(feats, Counter(
			{'i': 2, 'have': 2, 'that question': 1, 'answer': 1, 'question': 1, 'enough': 1, 'i have': 1,
			 'them specifically': 1, 'have enough': 1, 'not asked': 1, 'they have': 1,
			 'have not': 1, 'specifically': 1,
			 'answer that': 1, 'question i': 1, "can't": 1, 'if': 1, 'they': 1,
			 "can't answer": 1, 'asked': 1, 'them': 1,
			 'if they': 1, 'asked them': 1, 'that': 1, 'not': 1, "i can't": 1, 'specifically if': 1}))
