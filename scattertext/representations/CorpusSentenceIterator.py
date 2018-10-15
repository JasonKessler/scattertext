import itertools

from scattertext import ParsedCorpus


class CorpusSentenceIterator(object):
	@staticmethod
	def get_sentences(corpus):
		'''
		Parameters
		----------
		corpus, ParsedCorpus

		Returns
		-------
		iter: [sentence1word1, ...], [sentence2word1, ...]
		'''
		assert isinstance(corpus, ParsedCorpus)
		return itertools.chain(*[[[corpus._term_idx_store.getidxstrict(t.lower_) for t in sent
		                           if not t.is_punct]
		                          for sent in doc.sents]
		                         for doc in corpus.get_parsed_docs()])