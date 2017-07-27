from collections import Counter

from scattertext.emojis.EmojiExtractor import extract_emoji
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromSpacyDocOnlyEmoji(FeatsFromSpacyDoc):
	'''
	Strips away everything but emoji tokens from spaCy
	'''

	def get_feats(self, doc):
		'''
		Parameters
		----------
		doc, Spacy Docs

		Returns
		-------
		Counter emoji -> count
		'''
		return Counter(extract_emoji(str(doc)))
