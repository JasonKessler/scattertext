import re

from scattertext.emojis.ProcessedEmojiStructure import VALID_EMOJIS


'''
This is a fast but awful partial implementation of Spacy.   It's useful 
for testing and when you don't need POS tagging. 
'''


class Tok:
	def __init__(self, pos, lem, token, ent_type, tag, is_punct=False, idx=None):
		self.pos_ = pos
		self.lemma_ = lem
		self.lower_ = token.lower()
		self.orth_ = token
		self.ent_type_ = ent_type
		self.tag_ = tag
		self.is_punct = is_punct
		self.idx = idx

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
		self.toks = []
		for sent in sents:
			self.toks += sent

	def __str__(self):
		return self.string

	def __repr__(self):
		return self.string

	def __iter__(self):
		for sent in self.sents:
			for tok in sent:
				yield tok

	def __getitem__(self, idx):
		return self.toks[idx] # to do: make this more efficient by only having self.sents

	def __len__(self):
		return len(self.toks)


def whitespace_nlp(doc, entity_type=None, tag_type=None):
	toks = _regex_parse_sentence(doc, entity_type, tag_type)
	return Doc([toks])


def _regex_parse_sentence(doc, entity_type, tag_type):
	toks = _toks_from_sentence(doc, entity_type, tag_type)
	return toks

WHITESPACE_SPLITTER = re.compile(r"(\W)")

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



DEFAULT_TOK_SPLITTER_RE = re.compile(r'(\W)')

def whitespace_nlp_with_sentences(doc,
                                  entity_type=None,
                                  tag_type=None,
                                  tok_splitter_re=DEFAULT_TOK_SPLITTER_RE):
	sentence_split_pat = re.compile(r'([^\.!?]*?[\.!?$])', re.M)
	sents = []
	raw_sents = sentence_split_pat.findall(doc)
	if len(raw_sents) == 0:
		raw_sents = [doc]
	sent_start_idx = 0
	for sentence in raw_sents:
		toks = []
		start_idx_in_sentence = 0
		for tok in tok_splitter_re.split(sentence):
			if len(tok.strip()) > 0:
				toks.append(Tok(_get_pos_tag(tok),
				                tok[:2].lower(),
				                tok.lower(),
				                ent_type='' if entity_type is None else entity_type.get(tok, ''),
				                tag='' if tag_type is None else tag_type.get(tok, ''),
								idx=sent_start_idx + start_idx_in_sentence))
			start_idx_in_sentence += len(tok)
		sents.append(toks)
		sent_start_idx += len(sentence)
	return Doc(sents, doc)
