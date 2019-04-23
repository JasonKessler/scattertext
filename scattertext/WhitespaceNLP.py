import re

from scattertext.emojis.ProcessedEmojiStructure import VALID_EMOJIS

WHITESPACE_SPLITTER = re.compile(r"(\W)")

'''
This is a fast but awful partial implementation of Spacy.   It's useful 
for testing and when you don't need POS tagging. 
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
	def __init__(self, sents, raw=None, noun_chunks=[]):
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
	for tok in WHITESPACE_SPLITTER.split(doc):
		if len(tok) > 0:
			toks.append(Tok(_get_pos_tag(tok),
			                tok[:2].lower(),
			                tok.lower(),
			                ent_type='' if entity_type is None else entity_type.get(tok, ''),
			                tag='' if tag_type is None else tag_type.get(tok, '')))
	return toks


def nltk_tokenzier_factory(nltk_tokenizer):
	'''
	Parameters
	----------
	nltk_tokenizer : nltk.tokenize.* instance (e.g., nltk.TreebankWordTokenizer())

	Returns
	-------
	Doc of tweets

	Notes
	-------
	Requires NLTK to be installed
	'''

	def tokenize(text):
		toks = []
		for tok in nltk_tokenizer.tokenize(text):
			if len(tok) > 0:
				toks.append(Tok(_get_pos_tag(tok),
				                tok.lower(),
				                tok.lower(),
				                ent_type='',
				                tag=''))
		return Doc([toks], text)

	return tokenize


def tweet_tokenizier_factory(tweet_tokenizer):
	'''
	Parameters
	----------
	tweet_tokenizer

	Doc of tweets

	Notes
	-------
	Requires NLTK to be installed :(

	'''
	return nltk_tokenzier_factory(tweet_tokenizer)


PUNCT_MATCHER = re.compile('^\W+$')


def _get_pos_tag(tok):
	pos = 'WORD'
	if tok.strip() == '':
		pos = 'SPACE'
	elif ord(tok[0]) in VALID_EMOJIS:
		pos = 'EMJOI'
	elif PUNCT_MATCHER.match(tok):
		pos = 'PUNCT'
	return pos


def whitespace_nlp_with_sentences(doc,
                                  entity_type=None,
                                  tag_type=None,
                                  tok_splitter_re=WHITESPACE_SPLITTER):
	sentence_split_pat = re.compile(r'([^\.!?]*?[\.!?$])', re.M)
	sents = []
	raw_sents = sentence_split_pat.findall(doc)
	if len(raw_sents) == 0:
		raw_sents = [doc]
	for sent in raw_sents:
		toks = []
		for tok in tok_splitter_re.split(sent):
			if len(tok) > 0:
				toks.append(Tok(_get_pos_tag(tok),
				                tok[:2].lower(),
				                tok.lower(),
				                ent_type='' if entity_type is None else entity_type.get(tok, ''),
				                tag='' if tag_type is None else tag_type.get(tok, '')))
		sents.append(toks)
	return Doc(sents, doc)
