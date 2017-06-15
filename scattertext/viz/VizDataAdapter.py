import json
import sys

import numpy as np

from scattertext import AsianNLP
from scattertext import WhitespaceNLP


class MyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.integer):
			return int(obj)
		elif isinstance(obj, np.floating):
			return float(obj)
		elif isinstance(obj, np.ndarray):
			return obj.tolist()
		elif isinstance(obj, WhitespaceNLP.Doc):
			return repr(obj)
		elif isinstance(obj, AsianNLP.Doc):
			return repr(obj)
		elif 'spacy' in sys.modules:
			import spacy
			if isinstance(obj, spacy.tokens.doc.Doc):
				return repr(obj)
		else:
			return super(MyEncoder, self).default(obj)


class VizDataAdapter:
	def __init__(self, words_dict):
		self._word_dict = words_dict

	@property
	def word_dict(self):
		return self._word_dict

	@word_dict.setter
	def word_dict(self, val):
		self._word_dict = val

	@word_dict.deleter
	def word_dict(self):
		del self._word_dict

	def to_javascript(self):
		starter = 'function getDataAndInfo() { return'
		#import pdb;
		#pdb.set_trace()
		word_dict_json = json.dumps(self.word_dict, cls=MyEncoder)
		ender = '; }'
		return starter + word_dict_json + ender
