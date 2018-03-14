from collections import Counter

from scattertext import FeatsFromSpacyDoc


class UnigramsFromSpacyDoc(FeatsFromSpacyDoc):
	def get_feats(self, doc):
		'''
		Parameters
		----------
		doc, Spacy Docs

		Returns
		-------
		Counter (unigram, bigram) -> count
		'''
		ngram_counter = Counter()
		for sent in doc.sents:
			ngram_counter += Counter(self._get_unigram_feats(sent))
		return ngram_counter
