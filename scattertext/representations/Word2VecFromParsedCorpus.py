import itertools
import warnings
from collections import Counter

from scattertext.ParsedCorpus import ParsedCorpus


class FeatsFromGensim(object):
	def __init__(self, phrases, gram_size):
		'''
		Parameters
		----------
		phrases : list[gensim.models.Phrases]
		gram_size : int, maximum number of words per phrase
		kwargs : parameters for FeatsFromSpacyDoc.init
		'''
		from gensim.models import Phrases

		phrases = phrases
		gram_size = gram_size
		assert type(phrases) == Phrases
		self.gram_size = gram_size
		self.phrases = phrases

	def get_doc_metadata(self, doc):
		return Counter()

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
			ngrams = self.phrases[str(sent)]
			for subphrases in self.phrases[1:]:
				ngrams = subphrases[str(sent)]
			for ngram in ngrams:
				ngram_counter[ngram] += 1
		return ngram_counter


class GensimPhraseAdder(object):
	def __init__(self, max_tokens_per_phrase=3, phrases=None):
		'''
		Parameters
		----------
		max_tokens_per_phrase: int, must be > 1.  Default 3
		phrases: Instance of Gensim phrases class, default None
		'''
		self.max_tokens_per_phrase = max_tokens_per_phrase
		self.phrases = phrases

	def add_phrases(self, corpus):
		'''
		Parameters
		----------
		corpus: Corpus for phrase augmentation

		Returns
		-------
		New ParsedCorpus containing unigrams in corpus and new phrases
		'''
		from gensim.models import Phrases

		assert isinstance(corpus, ParsedCorpus)
		self.phrases = [Phrases(CorpusAdapterForGensim.get_sentences(corpus), delimiter=' ')]

		for i in range(1, self.max_tokens_per_phrase):
			self.phrases.append(Phrases(self.phrases[-1][CorpusAdapterForGensim.get_sentences(corpus)]))

		return self


class CorpusAdapterForGensim(object):
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
		return itertools.chain(*[[[t.lower_ for t in sent if not t.is_punct]
		                          for sent in doc.sents]
		                         for doc in corpus.get_parsed_docs()])


class Word2VecFromParsedCorpus(object):
	def __init__(self, corpus, word2vec_model=None):
		'''
		Parameters
		----------
		corpus: ParsedCorpus
		  from which to build word2vec model
		word2vec_model: word2vec.Word2Vec
			Gensim instance to be used to train word2vec model
		'''
		try:
			from gensim.models import word2vec
			assert word2vec_model is None or isinstance(word2vec_model, word2vec.Word2Vec)
		except:
			warnings.warn("You should really install gensim, but we're going to duck-type your model and pray it works")
		assert isinstance(corpus, ParsedCorpus)
		self.corpus = corpus
		self.model = self._get_word2vec_model(word2vec_model)

	def train(self, epochs=2000, training_iterations=5):
		'''
		Parameters
		----------
		epochs : int
		  Number of epochs to train for.  Default is 2000.
		training_iterations : int
			Number of times to repeat training process. Default is training_iterations.

		Returns
		-------
		A trained word2vec model.
		'''

		self._scan_and_build_vocab()
		for _ in range(training_iterations):
			self.model.train(CorpusAdapterForGensim.get_sentences(self.corpus),
			                 total_examples=self.model.corpus_count,
			                 epochs=epochs)
		return self.model

	def _get_word2vec_model(self, word2vec_model):
		return (self._default_word2vec_model()
		        if word2vec_model is None
		        else word2vec_model)

	def _default_word2vec_model(self):
		from gensim.models import word2vec
		return word2vec.Word2Vec(size=100,
		                         alpha=0.025,
		                         window=5,
		                         min_count=5,
		                         max_vocab_size=None,
		                         sample=0,
		                         seed=1,
		                         workers=1,
		                         min_alpha=0.0001,
		                         sg=1,
		                         hs=1,
		                         negative=0,
		                         cbow_mean=0,
		                         iter=1,
		                         null_word=0,
		                         trim_rule=None,
		                         sorted_vocab=1)

	def _scan_and_build_vocab(self):
		try:
			self.model.scan_vocab(CorpusAdapterForGensim.get_sentences(self.corpus))
		except:
			pass
		self.model.build_vocab(CorpusAdapterForGensim.get_sentences(self.corpus))


class Word2VecFromParsedCorpusBigrams(Word2VecFromParsedCorpus):
	def _scan_and_build_vocab(self):
		from gensim.models import Phrases
		bigram_transformer = Phrases(CorpusAdapterForGensim.get_sentences(self.corpus))
		try:
			self.model.scan_vocab(CorpusAdapterForGensim.get_sentences(self.corpus))
		except:
			pass
		self.model.build_vocab(bigram_transformer[CorpusAdapterForGensim.get_sentences(self.corpus)])
