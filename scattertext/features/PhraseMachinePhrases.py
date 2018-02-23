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
		ngram_counter = Counter()
		for sent in doc.sents:
			ngram_counter += _phrase_counts(sent)
		return ngram_counter


class PhraseMachinePhrasesAndUnigrams(FeatsFromSpacyDoc):
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
		# ngram_counter = phrasemachine.get_phrases(str(doc), tagger='spacy')['counts']
		ngram_counter = Counter()
		for sent in doc.sents:
			unigrams = self._get_unigram_feats(sent)
			ngram_counter += Counter(unigrams) + _phrase_counts(sent)
		return ngram_counter


def _phrase_counts(sent):
	pos_seq = [w.tag_ for w in sent]
	tokens = [w.lower_ for w in sent]
	counts = Counter()
	for (start, end) in phrasemachine.extract_ngram_filter(pos_seq, minlen=2, maxlen=8):
		phrase = phrasemachine.safejoin([tokens[i] for i in range(start, end)])
		phrase = phrase.lower()
		counts[phrase] += 1
	return counts
