from collections import Counter
from functools import partial

from scattertext import FeatsFromSpacyDoc


class FeatsFromSpacyDocAndEmpath(FeatsFromSpacyDoc):
	def __init__(self, empath_analyze_function=None, **kwargs):
		'''
		Parameters
		----------
		empath_analyze_function: function (default=empath.Empath().analyze)
			Function that produces a dictionary mapping Empath categories to

		Other parameters from FeatsFromSpacyDoc.__init__
		'''
		if empath_analyze_function is None:
			try:
				import empath
			except ImportError:
				raise Exception("Please install the empath library to use FeatsFromSpacyDocAndEmpath.")
			self._empath_analyze_function = empath.Empath().analyze
		else:
			self._empath_analyze_function = partial(empath_analyze_function,
			                                        kwargs={'tokenizer': 'bigram'})
		super(FeatsFromSpacyDocAndEmpath, self).__init__(**kwargs)

	def get_doc_metadata(self, doc, prefix=''):
		empath_counter = Counter()
		for empath_category, score in self._empath_analyze_function(str(doc)).items():
			if score > 0:
				empath_counter[prefix + empath_category] = int(score)
		return empath_counter
