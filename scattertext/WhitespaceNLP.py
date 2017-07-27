import re

from scattertext.emojis.ProcessedEmojiStructure import VALID_EMOJIS

'''
This is a fast but awful partial implementation of Spacy.  It's useful for testing.
'''


class Tok:
	def __init__(self, pos, lem, low, ent_type, tag, is_punct=False):
		self.pos_ = pos
		self.lemma_ = lem
		self.lower_ = low
		self.ent_type_ = ent_type
		self.tag_ = tag
		self.is_punct = is_punct

	def __str__(self):
		return self.lower_

	def __len__(self):
		return len(self.lower_)


class Doc:
	def __init__(self, sents, raw=None, noun_chunks = []):
		self.sents = sents
		if raw is None:
			self.string = ' '.join(
				''.join([tok.lower_ for tok in sent]) for sent in sents
			)
		else:
			self.string = raw
		self.text = self.string
		self.noun_chunks = noun_chunks

	def __str__(self):
		return self.string

	def __repr__(self):
		return self.string

	def __iter__(self):
		for sent in self.sents:
			for tok in sent:
				yield tok


def whitespace_nlp(doc, entity_type=None, tag_type=None):
	toks = _regex_parse_sentence(doc, entity_type, tag_type)
	return Doc([toks])




def _regex_parse_sentence(doc, entity_type, tag_type):
	toks = _toks_from_sentence(doc, entity_type, tag_type)
	return toks


def _toks_from_sentence(doc, entity_type, tag_type):
	toks = []
	for tok in re.split(r"(\W)", doc):
		pos = 'WORD'
		if tok.strip() == '':
			pos = 'SPACE'
		elif re.match('^\W+$', tok):
			pos = 'PUNCT'
		toks.append(Tok(pos,
		                tok[:2].lower(),
		                tok.lower(),
		                ent_type='' if entity_type is None else entity_type.get(tok, ''),
		                tag='' if tag_type is None else tag_type.get(tok, '')))
	return toks


def tweet_tokenzier_factory(tweet_tokenizer):
	'''
	Parameters
	----------
	tweet_tokenizer : nltk.tokenize.TweetTokenizer instance

	Returns
	-------
	Doc of tweets

	Notes
	-------
	Requires NLTK to be installed :(
	'''
	def tokenize(text):
		toks = []
		for tok in tweet_tokenizer.tokenize(text):
			pos = 'WORD'
			if tok.strip() == '':
				pos = 'SPACE'
			elif ord(tok[0]) in VALID_EMOJIS:
				pos = 'EMJOI'
			elif re.match('^\W+$', tok):
				pos = 'PUNCT'
			toks.append(Tok(pos,
			                tok.lower(),
			                tok.lower(),
			                ent_type='',
			                tag='' ))
		return Doc([toks], text)
	return tokenize


def whitespace_nlp_with_sentences(doc, entity_type=None, tag_type=None):
	pat = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
	sents = []
	for sent in pat.findall(doc):
		toks = []
		for tok in re.split(r"(\W)", sent):
			pos = 'WORD'
			if tok.strip() == '':
				pos = 'SPACE'
			elif re.match('^\W+$', tok):
				pos = 'PUNCT'
			toks.append(Tok(pos,
			                tok[:2].lower(),
			                tok.lower(),
			                ent_type='' if entity_type is None else entity_type.get(tok, ''),
			                tag='' if tag_type is None else tag_type.get(tok, '')))
		sents.append(toks)
		toks = []
	return Doc(sents, doc)
