import itertools

from gensim.models import word2vec, Phrases

from scattertext.ParsedCorpus import ParsedCorpus


class Word2VecFromParsedCorpus(object):
	def __init__(self, corpus, word2vec_model=None):
		assert isinstance(corpus, ParsedCorpus)
		assert word2vec_model is None or isinstance(word2vec_model, word2vec.Word2Vec)
		self.corpus = corpus
		self.model = self._get_word2vec_model(word2vec_model)

	def _get_word2vec_model(self, word2vec_model):
		return (self._default_word2vec_model()
		        if word2vec_model is None
		        else word2vec_model)

	def _default_word2vec_model(self):
		return word2vec.Word2Vec(size=100, alpha=0.025, window=5, min_count=5,
		                         max_vocab_size=None, sample=0, seed=1, workers=1, min_alpha=0.0001,
		                         sg=1, hs=1, negative=0, cbow_mean=0, iter=1, null_word=0,
		                         trim_rule=None, sorted_vocab=1)

	def train(self, epochs=2000):
		'''
		Parameters
		----------
		epochs int, number of epochs to train for.  Default is 2000.

		Returns
		-------
		A trained word2vec model.
		'''

		self._scan_and_build_vocab()
		self.model.train(self._get_line_sentences_for_word2vec(),
		                 total_examples=self.model.corpus_count,
		                 epochs=epochs)
		return self.model

	def _scan_and_build_vocab(self):
		self.model.scan_vocab(self._get_line_sentences_for_word2vec())
		self.model.build_vocab(self._get_line_sentences_for_word2vec())

	def _get_line_sentences_for_word2vec(self):
		return itertools.chain(*[[[t.lower_ for t in sent if not t.is_punct]
		                          for sent in doc.sents]
		                         for doc in self.corpus.get_parsed_docs()])


class Word2VecFromParsedCorpusBigrams(Word2VecFromParsedCorpus):
	def _scan_and_build_vocab(self):
		bigram_transformer = Phrases(self._get_line_sentences_for_word2vec())
		self.model.scan_vocab(bigram_transformer[self._get_line_sentences_for_word2vec()])
		self.model.build_vocab(bigram_transformer[self._get_line_sentences_for_word2vec()])
