from collections import Counter

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromSpacyDocOnlyNounChunks(FeatsFromSpacyDoc):
	'''
	Just returns noun chunks from spaCy
	'''

	def get_feats(self, doc):
		'''
		Parameters
		----------
		doc, Spacy Docs

		Returns
		-------
		Counter noun chunk -> count
		'''
		return Counter([str(c).lower() for c in doc.noun_chunks])
