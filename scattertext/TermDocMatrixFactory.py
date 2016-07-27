import string
from collections import Counter

import numpy as np
import spacy
from spacy.tokens.doc import Doc

from scattertext.CSRMatrixFactory import CSRMatrixFactory
from scattertext.IndexStore import IndexStore
from scattertext.TermDocMatrix import TermDocMatrix


class TermDocMatrixFactory:
	def __init__(self,
	             category_iter,
	             text_iter,
	             clean_function=lambda x: x,
	             nlp = None,
	             use_lemmas = False
	             ):
		"""Class for easy construction of a term document matrix.
		   This class let's you define an iterator for each document (text_iter),
		   an iterator for each document's category name (category_iter),
		   and a document cleaning function that's applied to each document
		   before it's parsed.

		   Parameters
		   ----------
		   text_iter : iter<unicode>
		       An iterator that iterates through the unicode text of each
		        document
		   category_iter : iter<str>
		       An iterator the same size as text iter that gives a string or
		       unicode name of each document catgory.  Defaults to the
		       identity function
		   clean_function : function (default lambda x: x)
		       A function that takes a unicode document and returns
		       a cleaned version of that document
		   nlp : spacy.en.English (default None)
		       The spaCy parser used to parse documents.  If it's None,
		       the class will go through the expensive operation of
		       creating one to parse the text
		   use_lemmas : bool (default False)
		       Do we use the lower-cased strings or lemmas from
		        the spaCy tokenization?
		   Attributes
		   ----------
		   _clean_function : function
		       function that takes a unicode document and returns
		       a cleaned version of that document
		   _text_iter : iter<unicode>
		       an iterator that iterates through the unicode text of each
		        document
		   _category_iter : iter<str>
		       an iterator the same size as text iter that gives a string or
		       unicode name of each document catgory
		   Examples
		   --------
		   >>> import scattertext as TI
		   >>> documents = [u"What art thou that usurp'st this time of night,",
		    u'Together with that fair and warlike form',
		    u'In which the majesty of buried Denmark',
		    u'Did sometimes march? by heaven I charge thee, speak!',
				u'Halt! Who goes there?',
				u'[Intro]',
				u'It is I sire Tone from Brooklyn.',
				u'Well, speak up man what is it?',
				u'News from the East sire! THE BEST OF BOTH WORLDS HAS RETURNED!'
		    ]
		   >>> categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5
		   >>> clean_function = lambda text: '' if text.startswith('[') else text
		   >>> term_doc_mat = TI.TermDocMatrixFactory(
		    category_iter = categories,
		    iter_text = documents,
		    clean_function = clean_function
		   ).build()

		"""
		self._category_iter = category_iter
		self._text_iter = text_iter
		self._clean_function = clean_function
		self._nlp = nlp
		self._use_lemmas = use_lemmas

	def build(self):
		"""Generate a TermDocMatrix from data in parameters.

		 Returns
		 ----------
		 term_doc_matrix : TermDocMatrix
		    The object that this factory class builds.
		"""
		nlp = self._nlp
		if nlp is None:
			nlp = spacy.en.English()

		category_document_iter = (
			(category, self._clean_function(raw_text))
			for category, raw_text
			in zip(self._category_iter, self._text_iter)
		)
		term_doc_matrix = self._build_from_category_spacy_doc_iter(
			(
				(category, nlp(text))
				for (category, text)
				in category_document_iter
				if text.strip() != ''
			)
		)
		return term_doc_matrix

	def _build_from_category_spacy_doc_iter(self, category_doc_iter):
		'''
		:param category_doc_iter: iterator of (string category name, spacy.tokens.doc.Doc) pairs
		:return: TermDocMatrix
		'''
		y = []
		X_factory = CSRMatrixFactory()
		term_idx_store = IndexStore()
		category_idx_store = IndexStore()
		for doci, (category, parsed_text) in enumerate(category_doc_iter):
			y.append(category_idx_store.getidx(category))
			term_freq = Counter()
			for sent in parsed_text.sents:
				unigrams = []
				for tok in sent:
					if tok.pos_ not in ('PUNCT', 'SPACE', 'X'):
						if self._use_lemmas:
							if tok.lemma_.strip():
								unigrams.append(tok.lemma_.strip())
						else:
							if tok.lower_.strip():
								unigrams.append(tok.lower_.strip())
				bigrams = map(' '.join, zip(unigrams[:-1], unigrams[1:]))
				for term in unigrams + bigrams:
					term_freq[term_idx_store.getidx(term)] += 1
			for word_idx, freq in term_freq.items():
				X_factory[doci, word_idx] = freq

		return TermDocMatrix(X=X_factory.get_csr_matrix(),
		                     y=np.array(y),
		                     term_idx_store=term_idx_store,
		                     category_idx_store=category_idx_store)



def build_from_category_whitespace_delimited_text(category_text_iter):
	'''
	:param category_text_iter: iterator of (string category name, one line per sentence, whitespace-delimited text) pairs
	:return: TermDocMatrix
	'''
	y = []
	X_factory = CSRMatrixFactory()
	term_idx_store = IndexStore()
	category_idx_store = IndexStore()
	for doci, (category, text) in enumerate(category_text_iter):
		assert type(category) in [str, unicode]
		assert type(text) in [str, unicode]
		y.append(category_idx_store.getidx(category))
		term_freq = Counter()
		for sent in text.strip(string.punctuation).lower().split('\n'):
			unigrams = []
			for tok in sent.strip().split():
				unigrams.append(tok)
			bigrams = map(' '.join, zip(unigrams[:-1], unigrams[1:]))
			for term in unigrams + bigrams:
				term_freq[term_idx_store.getidx(term)] += 1
		for word_idx, freq in term_freq.items():
			X_factory[doci, word_idx] = freq

	return TermDocMatrix(X=X_factory.get_csr_matrix(),
	                     y=np.array(y),
	                     term_idx_store=term_idx_store,
	                     category_idx_store=category_idx_store)