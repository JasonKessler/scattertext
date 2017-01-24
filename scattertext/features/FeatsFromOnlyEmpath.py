from collections import Counter

from scattertext.features.FeatsFromSpacyDocAndEmpath import FeatsFromSpacyDocAndEmpath


class FeatsFromOnlyEmpath(FeatsFromSpacyDocAndEmpath):
	def get_feats(self, doc):
		return Counter()
	def get_doc_metadata(self, doc, prefix=''):
		return super(FeatsFromOnlyEmpath, self).get_doc_metadata(doc, prefix=prefix)