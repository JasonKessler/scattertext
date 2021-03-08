from scattertext.features.FeatsFromSpacyDocAndEmpath import FeatsFromSpacyDocAndEmpath
from collections import Counter


class FeatsFromOnlyEmpath(FeatsFromSpacyDocAndEmpath):
	def get_feats(self, doc):
		return Counter()
	def get_doc_metadata(self, doc, prefix=''):
		return FeatsFromSpacyDocAndEmpath.get_doc_metadata(self, doc, prefix=prefix)


