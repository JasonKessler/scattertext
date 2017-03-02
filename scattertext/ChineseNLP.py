# -*- coding: utf-8 -*-
import re

import jieba

'''
I don't speak Chinese, but implemented a very simple sentence splitter.  Assistance would be greatly appreciated.
'''


class Tok(object):
	def __init__(self, pos, lem, orth, low, ent_type, tag):
		self.pos_ = pos
		self.lemma_ = lem
		self.lower_ = low
		self.orth_ = orth
		self.ent_type_ = ent_type
		self.tag_ = tag
	def __repr__(self): return self.orth_
	def __str__(self): return self.orth_


class Doc(object):
	def __init__(self, sents, raw):
		self.sents = sents
		self.string = raw
		self.text = raw
	def __str__(self):
		return '\n'.join(str(sent) for sent in self.sents)
	def __repr__(self):
		return self.__str__()
	def __iter__(self):
		for sent in self.sents:
			for tok in sent:
				yield tok


class Sentence(object):
	def __init__(self, toks, raw):
		self.toks = toks
		self.raw = raw
	def __iter__(self):
		for tok in self.toks:
			yield tok
	def __str__(self):
		return ' '.join([str(tok) for tok in self.toks])
	def __repr__(self):
		return self.raw

punct_re = re.compile(r'^(\?|!|:|,|\.|【|】|［|］|（|）|：|；|，|？|。|」|！|﹂|”|"|_|﹏|《|》|〈|〉|‧|、|「|」|﹁|﹂|"|"|～|—|—)+$')

def chinese_nlp(doc, entity_type=None, tag_type=None):
	sents = []
	for paragraph in doc.split('\n'):
		sent_splits = iter(re.split(r'(？|。|」|！)+', paragraph, flags=re.MULTILINE))
		for partial_sent in sent_splits:
			sent = partial_sent + next(sent_splits,'')
			if sent.strip() == '': continue
			toks = []
			for tok in jieba.cut(sent, ):
				pos = 'WORD'
				if tok.strip() == '':
					pos = 'SPACE'
				elif punct_re.match(tok):
					pos = 'PUNCT'
				toks.append(Tok(pos,
				                tok[:2].lower(),
				                tok.lower(),
				                tok,
				                ent_type='' if entity_type is None else entity_type.get(tok, ''),
				                tag='' if tag_type is None else tag_type.get(tok, '')))
			sents.append(Sentence(toks, sent))
	return Doc(sents, doc)