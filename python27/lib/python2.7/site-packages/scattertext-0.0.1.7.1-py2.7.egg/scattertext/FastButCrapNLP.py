import re


class Tok:
	def __init__(self, pos, lem, low, ent_type):
		self.pos_ = pos
		self.lemma_ = lem
		self.lower_ = low
		self.ent_type_ = ent_type


class Doc:
	def __init__(self, sents):
		self.sents = sents


def fast_but_crap_nlp(doc):
	toks = []
	for tok in re.split(r"(\W)", doc):
		pos = 'WORD'
		if tok.strip() == '':
			pos = 'SPACE'
		elif re.match('^\W+$', tok):
			pos = 'PUNCT'
		toks.append(Tok(pos, tok[:2].lower(), tok.lower(), ''))
	return Doc([toks])