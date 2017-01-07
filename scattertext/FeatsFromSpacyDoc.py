from collections import Counter
from itertools import chain


class FeatsFromSpacyDoc(object):
	def __init__(self,
	             use_lemmas=False,
	             entity_types_to_censor=set(),
	             tag_types_to_censor=set()):
		'''
		Parameters
		----------
		use_lemmas : bool, optional
			False by default
		entity_types_to_censor : set
			empty by default
		tag_types_to_censor : set
			empty by default
		'''
		self._use_lemmas = use_lemmas
		assert type(entity_types_to_censor) == set
		assert type(tag_types_to_censor) == set
		self._entity_types_to_censor = entity_types_to_censor
		self._tag_types_to_censor = tag_types_to_censor


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
			unigrams = []
			for tok in sent:
				if tok.pos_ not in ('PUNCT', 'SPACE', 'X'):
					if tok.ent_type_ in self._entity_types_to_censor:
						unigrams.append(tok.ent_type_)
					elif tok.tag_ in self._tag_types_to_censor:
						unigrams.append(tok.tag_)
					elif self._use_lemmas and tok.lemma_.strip():
							unigrams.append(tok.lemma_.strip())
					elif tok.lower_.strip():
						unigrams.append(tok.lower_.strip())
			if len(unigrams) > 1:
				bigrams = map(' '.join, zip(unigrams[:-1], unigrams[1:]))
			else:
				bigrams = []
			ngram_counter += Counter(chain(unigrams, bigrams))
		return ngram_counter