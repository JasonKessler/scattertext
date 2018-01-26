from collections import Counter

from scattertext.external.phrasemachine import phrasemachine
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class PhraseMachinePhrases(FeatsFromSpacyDoc):
	'''
	Returns unigrams and phrase machine phrases
	'''

	def get_feats(self, doc):
		'''
		Parameters
		----------
		doc, Spacy Doc

		Returns
		-------
		Counter noun chunk -> count
		'''
		ngram_counter = phrasemachine.get_phrases(str(doc), tagger='spacy')['counts']
		for sent in doc.sents:
			unigrams = self._get_unigram_feats(sent)
			ngram_counter += Counter(unigrams)
		return ngram_counter
