"""
Noun phrase extraction using Python's regular expression library.
Only for the "SimpleNP" grammar.



"""
from __future__ import print_function

import os
import re
import sys
from collections import Counter

#from pkg_resources import resource_filename


def logmsg(s):
	# would be better to use python logger
	print("[phrasemachine] %s" % s, file=sys.stderr)


if sys.version_info[0] >= 3:
	xrange = range

############## SimpleNP
## Uses a five-tag coarse grammar.
## tagset: A D P N O

# Requires conversion from PTB or Petrov/Gimpel tags to our system.
# "Coarse*" indicates petrov/gimpel
# Grammar change from the FST version: can't repeat NUM in both adj and noun.
coarsemap = {
	'A': "JJ JJR JJS CoarseADJ CD CoarseNUM".split(),
	'D': "DT CoarseDET".split(),
	'P': "IN TO CoarseADP".split(),
	'N': "NN NNS NNP NNPS FW CoarseNOUN".split(),
	# all other tags get O
}

## OLDER ATTEMPT: tried to use direct tags as port from foma.
## but this was annoying. have to map back to token positions at the end.
## probably slower too since the python regex compiler is not as smart as foma
# def regex_or(items):
#     return '|'.join(re.escape(x) for x in items)
# Adj = regex_or("JJ JJR JJS CD CoarseADJ CoarseNUM".split())
# Det = regex_or("DT CoarseDET".split())
# Prep= regex_or("IN TO CoarseADP".split())
# Noun= regex_or("NN NNS NNP NNPS FW CD CoarseNOUN CoarseNUM".split())
# ## convention: SPACES separate tags.
# BaseNP = "(({Adj}|{Noun}) )*({Noun} )+".format(**globals())
# PP     = "{Prep} ({Det} )*{BaseNP}".format(**globals())
# NP     = "{BaseNP}({PP} )*".format(**globals())

tag2coarse = {}
for coarsetag, inputtags in coarsemap.items():
	for intag in inputtags:
		assert intag not in tag2coarse
		tag2coarse[intag] = coarsetag

## The grammar!
SimpleNP = "(A|N)*N(PD*(A|N)*N)*"


def coarse_tag_str(pos_seq):
	"""Convert POS sequence to our coarse system, formatted as a string."""
	global tag2coarse
	tags = [tag2coarse.get(tag, 'O') for tag in pos_seq]
	return ''.join(tags)


# POS extraction assuming list of POS tags as input.
# >>> pyre.extract_finditer(["VB","JJ","NN","NN","QQ","QQ",])
# [(1, 4)]
# >>> pyre.extract_ngram_filter(["VB","JJ","NN","NN","QQ","QQ",])
# [(1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]

def extract_finditer(pos_seq, regex=SimpleNP):
	"""The "GreedyFSA" method in Handler et al. 2016.
	Returns token position spans of valid ngrams."""
	ss = coarse_tag_str(pos_seq)

	def gen():
		for m in re.finditer(regex, ss):
			yield (m.start(), m.end())

	return list(gen())


def extract_ngram_filter(pos_seq, regex=SimpleNP, minlen=1, maxlen=8):
	"""The "FilterFSA" method in Handler et al. 2016.
	Returns token position spans of valid ngrams."""
	ss = coarse_tag_str(pos_seq)

	def gen():
		for s in xrange(len(ss)):
			for n in xrange(minlen, 1 + min(maxlen, len(ss) - s)):
				e = s + n
				substr = ss[s:e]
				if re.match(regex + "$", substr):
					yield (s, e)

	return list(gen())


def extract_JK(pos_seq):
	"""The 'JK' method in Handler et al. 2016.
	Returns token positions of valid ngrams."""

	def find_ngrams(input_list, num_):
		'''get ngrams of len n from input list'''
		return zip(*[input_list[i:] for i in range(num_)])

	# copied from M and S chp 5'''
	patterns = set(['AN', 'NN', 'AAN', 'ANN', 'NAN', 'NNN', 'NPN'])
	pos_seq = [tag2coarse.get(tag, 'O') for tag in pos_seq]
	pos_seq = [(i, p) for i, p in enumerate(pos_seq)]
	ngrams = [ngram for n in range(1, 4) for ngram in find_ngrams(pos_seq, n)]

	def stringify(s):
		return "".join(a[1] for a in s)

	def positionify(s):
		return tuple(a[0] for a in s)

	ngrams = filter(lambda x: stringify(x) in patterns, ngrams)
	return [set(positionify(n)) for n in ngrams]


########

def unicodify(s, encoding='utf8', errors='ignore'):
	# Force conversion to unicode
	if sys.version_info[0] < 3:
		if isinstance(s, unicode): return s
		if isinstance(s, str): return s.decode(encoding, errors)
		return unicode(s)
	else:
		if type(s) == bytes:
			return s.decode('utf8')
		else:
			return s


def safejoin(list_of_str_or_unicode):
	## can accept a list of str objects, or a list of unicodes.
	## safely joins them, returning the same type.
	xx = list_of_str_or_unicode
	if not xx:
		return u""
	if isinstance(xx[0], str):
		return ' '.join(xx)

	if isinstance(xx[0], bytes):
		return ' '.join(xx)

	if sys.version_info[0] < 3:
		if isinstance(xx[0], unicode):
			return u' '.join(xx)

	raise Exception("Bad input to safejoin:", list_of_str_or_unicode)


#########

class NLTKTagger:
	'''
	class that supplies part of speech tags using NLTK
	note: avoids the NLTK downloader (see __init__ method)
	'''

	def __init__(self):
		import nltk
		from nltk.tag import PerceptronTagger
		from nltk.tokenize import TreebankWordTokenizer
		#return pkgutil.get_data('scattertext',
		#                        'data/viz/semiotic_new.html').decode('utf-8')
		path = os.path.dirname(sys.modules['scattertext'].__file__)+'/data/'
		tokenizer_fn = path + 'punkt.english.pickle'
		tagger_fn = path + 'averaged_perceptron_tagger.pickle'
		#tokenizer_fn = os.path.abspath(resource_filename('scattertext.data', 'punkt.english.pickle'))
		#tagger_fn = os.path.abspath(resource_filename('scattertext.data', 'averaged_perceptron_tagger.pickle'))
		# Load the tagger
		self.tagger = PerceptronTagger(load=False)
		self.tagger.load(tagger_fn)

		# note: nltk.word_tokenize calls the TreebankWordTokenizer, but uses the downloader.
		#       Calling the TreebankWordTokenizer like this allows skipping the downloader.
		#       It seems the TreebankWordTokenizer uses PTB tokenization = regexes. i.e. no downloads
		#       https://github.com/nltk/nltk/blob/develop/nltk/tokenize/treebank.py#L25
		self.tokenize = TreebankWordTokenizer().tokenize
		self.sent_detector = nltk.data.load(tokenizer_fn)

	# http://www.nltk.org/book/ch05.html
	def tag_text(self, text):
		'''take input text and return tokens w/ part of speech tags using NLTK'''
		# putting import here instead of top of file b.c. not all will have nltk installed

		sents = self.sent_detector.tokenize(text)  # TODO: this will fail on some unicode chars. I think assumes ascii
		word_pos_pairs = []

		all_tokens = []
		for sent in sents:
			tokens = self.tokenize(sent)
			all_tokens = all_tokens + tokens
			word_pos_pairs = word_pos_pairs + self.tagger.tag(tokens)
		return {'tokens': all_tokens, 'pos': [tag for (w, tag) in word_pos_pairs]}

	def tag_tokens(self, tokens):
		word_pos_pairs = self.tagger.tag(tokens)
		return {'tokens': tokens, 'pos': [tag for (w, tag) in word_pos_pairs]}


def get_stdeng_nltk_tagger(suppress_errors=False):
	try:
		tagger = NLTKTagger()
		throw_away = tagger.tag_text("The red cat sat down.")
		return NLTKTagger()
	except ImportError:
		if not suppress_errors: raise
	except LookupError:
		if not suppress_errors: raise
	return None


SPACY_WRAPPER = None


class SpacyTagger:
	# https://spacy.io/
	def __init__(self):
		self.spacy_object = None

	def tag_text(self, text):
		text = unicodify(text)
		doc = self.spacy_object(text)
		return {
			'pos': [token.tag_ for token in doc],
			'tokens': [token.text for token in doc],
		}

	def tag_tokens(self, tokens):
		# tokens: a list of strings
		# todo: would be better to force spacy to use the given tokenization
		newtext = safejoin(tokens)
		newtext = unicodify(newtext)  ## spacy wants unicode objects only. problem if user gave us a string.
		return self.tag_text(newtext)


def get_stdeng_spacy_tagger(suppress_errors=False):
	global SPACY_WRAPPER
	if SPACY_WRAPPER is not None:
		return SPACY_WRAPPER
	try:
		import spacy
		SPACY_WRAPPER = SpacyTagger()
		SPACY_WRAPPER.spacy_object = spacy.load('en', parser=False, entity=False)
		return SPACY_WRAPPER
	except ImportError:
		if not suppress_errors: raise
	except RuntimeError:
		## this seems to happen if the 'en' model is not installed. it might
		## look like this:
		# RuntimeError: Model 'en' not installed. Please run 'python -m spacy.en.download' to install latest compatible model.
		if not suppress_errors: raise
	return None


TAGGER_NAMES = {
	'nltk': get_stdeng_nltk_tagger,
	'spacy': get_stdeng_spacy_tagger,
	# 'twitter': None,
}


def get_phrases(text=None, tokens=None, postags=None, tagger='nltk', grammar='SimpleNP', regex=None, minlen=2, maxlen=8,
                output='counts'):
	"""Give a text (or POS tag sequence), return the phrases matching the given
	grammar.  Works on documents or sentences.
	Returns a dict with one or more keys with the phrase information.

	text: the text of the document.  If supplied, we will try to POS tag it.

	You can also do your own tokenzation and/or tagging and supply them as
	'tokens' and/or 'postags', which are lists of strings (of the same length).
	 - Must supply both to get phrase counts back.
	 - With only postags, can get phrase token spans back.
	 - With only tokens, we will try to POS-tag them if possible.

	output: a string, or list of strings, of information to return. Options include:
	 - counts: a Counter with phrase frequencies.  (default)
	 - token_spans: a list of the token spans of each matched phrase.  This is
		 a list of (start,end) pairs of integers, which refer to token positions.
	 - pos, tokens can be returned too.

	tagger: if you're passing in raw text, can supply your own tagger, from one
	of the get_*_tagger() functions.  If this is not supplied, we will try to load one.

	grammar: the grammar to use.  Only one option right now...

	regex: a custom regex to use, instead of a premade grammar.  Currently,
	this must work on the 5-tag system described near the top of this file.

	"""
	global SimpleNP

	## try to get values for both 'postags' and 'tokens', parallel lists of strings
	if postags is None:
		try:
			tagger = TAGGER_NAMES[tagger]()
		except:
			raise Exception("We don't support tagger %s" % tagger)
		# otherwise, assume it's one of our wrapper *Tagger objects

		d = None
		if tokens is not None:
			d = tagger.tag_tokens(tokens)
		elif text is not None:
			d = tagger.tag_text(text)
		else:
			raise Exception("Need to supply text or tokens.")
		postags = d['pos']
		tokens = d['tokens']

	if regex is None:
		if grammar == 'SimpleNP':
			regex = SimpleNP
		else:
			assert False, "Don't know grammar %s" % grammar

	phrase_tokspans = extract_ngram_filter(postags, minlen=minlen, maxlen=maxlen)

	## Handle multiple possible return info outputs

	if isinstance(output, str):
		output = [output]

	our_options = set()

	def retopt(x):
		our_options.add(x)
		return x in output

	ret = {}
	ret['num_tokens'] = len(postags)
	if retopt('token_spans'):
		ret['token_spans'] = phrase_tokspans
	if retopt('counts'):
		counts = Counter()
		for (start, end) in phrase_tokspans:
			phrase = safejoin([tokens[i] for i in xrange(start, end)])
			phrase = phrase.lower()
			counts[phrase] += 1
		ret['counts'] = counts
	if retopt('pos'):
		ret['pos'] = postags
	if retopt('tokens'):
		ret['tokens'] = tokens

	xx = set(output) - our_options
	if xx:
		raise Exception("Don't know how to handle output options: %s" % list(xx))
	return ret
