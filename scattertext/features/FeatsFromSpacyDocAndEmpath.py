from collections import Counter
from functools import partial
from sys import version_info

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromSpacyDocAndEmpath(FeatsFromSpacyDoc):
	def __init__(self,
	             use_lemmas=False,
	             entity_types_to_censor=set(),
	             tag_types_to_censor=set(),
	             strip_final_period=False,
	             empath_analyze_function=None,
	             **kwargs):
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
		super(FeatsFromSpacyDocAndEmpath, self).__init__(use_lemmas,
		                                                 entity_types_to_censor,
		                                                 tag_types_to_censor,
		                                                 strip_final_period)

	def get_doc_metadata(self, doc, prefix=''):
		empath_counter = Counter()
		if version_info[0] >= 3:
			doc = str(doc)
		for empath_category, score in self._empath_analyze_function(doc).items():
			if score > 0:
				empath_counter[prefix + empath_category] = int(score)
		return empath_counter
