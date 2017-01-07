import re

'''
This is a fast buf awful partial implementation of Spacy.  It's useful for testing.
'''

class Tok:
	def __init__(self, pos, lem, low, ent_type, tag):
		self.pos_ = pos
		self.lemma_ = lem
		self.lower_ = low
		self.ent_type_ = ent_type
		self.tag_ = tag


class Doc:
	def __init__(self, sents):
		self.sents = sents
		self.string = ' '.join(
			''.join([tok.lower_ for tok in sent]) for sent in sents
		)
		self.text = self.string

	def __str__(self):
		return self.string


def fast_but_crap_nlp(doc, entity_type=None, tag_type=None):
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
	return Doc([toks])
