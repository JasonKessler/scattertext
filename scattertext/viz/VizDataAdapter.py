import json

import numpy as np


# from http://stackoverflow.com/questions/27050108/convert-numpy-type-to-python/27050186#27050186
class MyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.integer):
			return int(obj)
		elif isinstance(obj, np.floating):
			return float(obj)
		elif isinstance(obj, np.ndarray):
			return obj.tolist()
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
		word_dict_json = json.dumps(self.word_dict)
		ender = '; }'
		return starter + word_dict_json + ender
