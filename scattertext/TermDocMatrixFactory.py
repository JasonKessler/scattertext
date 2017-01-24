import string
from collections import Counter

import numpy as np

from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.IndexStore import IndexStore
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class CategoryTextIterNotSetError(Exception):
	pass


class TermDocMatrixFactory(object):
	def __init__(self,
	             category_text_iter=None,
	             clean_function=lambda x: x,
	             nlp=None,
	             feats_from_spacy_doc=None
	             ):
		"""
		Class for easy construction of a term document matrix.
	   This class let's you define an iterator for each document (text_iter),
	   an iterator for each document's category name (category_iter),
	   and a document cleaning function that's applied to each document
	   before it's parsed.

	   Parameters
	   ----------
	   category_text_iter : iter<str: category, unicode: document)>
	       An iterator of pairs. The first element is a string category
	       name, the second the text of a document.  You can also set this
	       using the function set_category_text_iter.
	   clean_function : function (default lambda x: x)
	       A function that takes a unicode document and returns
	       a cleaned version of that document
	   post_nlp_clean_function : function (default lambda x: x)
	       A function that takes a spaCy Doc
	   nlp : spacy.en.English (default None)
	       The spaCy parser used to parse documents.  If it's None,
	       the class will go through the expensive operation of
	       creating one to parse the text
	   feats_from_spacy_doc : FeatsFromSpacyDoc (default None)
	       Class for extraction of features from spacy
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
	   >>> import scattertext as ST
	   >>> documents = [u'What art thou that usurp''st this time of night,',
	   ...u'Together with that fair and warlike form',
	   ...u'In which the majesty of buried Denmark',
	   ...u'Did sometimes march? by heaven I charge thee, speak!',
		 ...u'Halt! Who goes there?',
		 ...u'[Intro]',
		 ...u'It is I sire Tone from Brooklyn.',
		 ...u'Well, speak up man what is it?',
		 ...u'News from the East sire! THE BEST OF BOTH WORLDS HAS RETURNED!']
	   >>> categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5
	   >>> clean_function = lambda text: '' if text.startswith('[') else text
	   >>> term_doc_mat = ST.TermDocMatrixFactory(category_text_iter = zip(categories, documents),clean_function = clean_function).build()
		"""
		self._category_text_iter = category_text_iter
		self._clean_function = clean_function
		self._nlp = nlp
		self._entity_types_to_censor = set()
		if feats_from_spacy_doc is None:
			self._feats_from_spacy_doc = FeatsFromSpacyDoc()
		else:
			self._feats_from_spacy_doc = feats_from_spacy_doc

	def set_category_text_iter(self, category_text_iter):
		"""Initializes the category_text_iter

	   Paramters
	   ----------
	   category_text_iter : iter<str: category, unicode: document)>
		       An iterator of pairs. The first element is a string category
		       name, the second the text of a document.

		 Returns
		 ----------
		 self: TermDocMatrixFactory
		"""

		self._category_text_iter = category_text_iter
		return self

	def set_nlp(self, nlp):
		"""Adds a spaCy-compatible nlp function

	   Paramters
	   ----------
	   nlp : spacy.en.English

		 Returns
		 ----------
		 self: TermDocMatrixFactory
		"""

		self._nlp = nlp
		return self

	def build(self):
		"""Generate a TermDocMatrix from data in parameters.

		 Returns
		 ----------
		 term_doc_matrix : TermDocMatrix
		    The object that this factory class builds.
		"""
		if self._category_text_iter is None:
			raise CategoryTextIterNotSetError()
		nlp = self.get_nlp()

		category_document_iter = (
			(category, self._clean_function(raw_text))
			for category, raw_text
			in self._category_text_iter
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

	def get_nlp(self):
		nlp = self._nlp
		if nlp is None:
			import spacy.en
			nlp = spacy.en.English()
		return nlp

	def censor_entity_types(self, entity_types):
		# type: (set) -> TermDocMatrixFactory
		'''
		Entity types to exclude from feature construction. Terms matching
		specificed entities, instead of labeled by their lower case orthographic
		form or lemma, will be labeled by their entity type.

		Parameters
		----------
		entity_types : set of entity types outputted by spaCy
		  'TIME', 'WORK_OF_ART', 'PERSON', 'MONEY', 'ORG', 'ORDINAL', 'DATE',
		  'CARDINAL', 'LAW', 'QUANTITY', 'GPE', 'PERCENT'

		Returns
		---------
		self
		'''
		assert type(entity_types) == set
		self._entity_types_to_censor = entity_types
		self._feats_from_spacy_doc = FeatsFromSpacyDoc(
			use_lemmas=self._use_lemmas,
			entity_types_to_censor=self._entity_types_to_censor
		)
		return self

	def _build_from_category_spacy_doc_iter(self, category_doc_iter):
		'''
		Parameters
		----------
		category_doc_iter : iterator of (string category name, spacy.tokens.doc.Doc) pairs

		Returns
		----------
		t : TermDocMatrix
		'''
		term_idx_store = IndexStore()
		category_idx_store = IndexStore()
		metadata_idx_store = IndexStore()
		X, mX, y = self._get_features_and_labels_from_documents_and_indexes(category_doc_iter,
		                                                                    category_idx_store,
		                                                                    term_idx_store,
		                                                                    metadata_idx_store)
		return TermDocMatrix(X,
		                     mX,
		                     y,
		                     term_idx_store=term_idx_store,
		                     category_idx_store=category_idx_store,
		                     metadata_idx_store=metadata_idx_store)

	def _get_features_and_labels_from_documents_and_indexes(self,
	                                                        category_doc_iter,
	                                                        category_idx_store,
	                                                        term_idx_store,
	                                                        metadata_idx_store):
		y = []
		X_factory = CSRMatrixFactory()
		mX_factory = CSRMatrixFactory()
		for document_index, (category, parsed_text) in enumerate(category_doc_iter):
			self._register_doc_and_category(X_factory,
			                                mX_factory,
			                                category,
			                                category_idx_store,
			                                document_index,
			                                parsed_text,
			                                term_idx_store,
			                                metadata_idx_store,
			                                y)
		X = X_factory.get_csr_matrix()
		mX = mX_factory.get_csr_matrix()
		y = np.array(y)
		return X, mX, y

	def _old_register_doc_and_category(self,
	                                   X_factory,
	                                   category, category_idx_store,
	                                   document_index,
	                                   parsed_text,
	                                   term_idx_store,
	                                   y):
		y.append(category_idx_store.getidx(category))
		document_features = self._get_features_from_parsed_text(parsed_text, term_idx_store)
		self._register_document_features_with_X_factory \
			(X_factory, document_index, document_features)

	def _register_doc_and_category(self,
	                               X_factory,
	                               mX_factory,
	                               category,
	                               category_idx_store,
	                               document_index,
	                               parsed_text,
	                               term_idx_store,
	                               metadata_idx_store,
	                               y):
		y.append(category_idx_store.getidx(category))
		for term, count in self._feats_from_spacy_doc.get_feats(parsed_text).items():
			term_idx = term_idx_store.getidx(term)
			X_factory[document_index, term_idx] = count
		for term, val in self._feats_from_spacy_doc.get_doc_metadata(parsed_text).items():
			meta_idx = metadata_idx_store.getidx(term)
			X_factory[document_index, meta_idx] = val

	def _register_document_features_with_X_factory(self, X_factory, doci, term_freq):
		for word_idx, freq in term_freq.items():
			X_factory[doci, word_idx] = freq

	def _get_features_from_parsed_text(self, parsed_text, term_idx_store):
		return {term_idx_store.getidxstrict(k):v for k, v
		        in self._feats_from_spacy_doc.get_feats(parsed_text).items()
		        if k in term_idx_store}



class FeatsFromDoc(TermDocMatrixFactory):
	def __init__(self,
	             term_idx_store,
	             clean_function=lambda x: x,
	             nlp=None,
	             feats_from_spacy_doc = None):
		"""Class for extracting features from a new document.

	   Parameters
	   ----------
	   term_idx_store : IndexStore (index -> term)
	   clean_function : function (default lambda x: x)
	       A function that takes a unicode document and returns
	       a cleaned version of that document
	   post_nlp_clean_function : function (default lambda x: x)
	       A function that takes a spaCy Doc
	   nlp : spacy.en.English (default None)
	       The spaCy parser used to parse documents.  If it's None,
	       the class will go through the expensive operation of
	       creating one to parse the text
	   feats_from_spacy_doc : FeatsFromSpacyDoc (default None)
	       Class for extraction of features from spacy

	   """
		TermDocMatrixFactory.__init__(self,
		                              clean_function=clean_function,
		                              nlp=nlp,
		                              feats_from_spacy_doc=feats_from_spacy_doc)
		self._term_idx_store = term_idx_store

	def feats_from_doc(self, raw_text):
		'''
		Parameters
		----------
		raw_text, uncleaned text for parsing out features

		Returns
		-------
		csr_matrix, feature matrix
		'''
		parsed_text = self._nlp(self._clean_function(raw_text))
		X_factory = CSRMatrixFactory()
		X_factory.set_last_col_idx(self._term_idx_store.getnumvals() - 1)
		term_freq = self._get_features_from_parsed_text(parsed_text, self._term_idx_store)
		self._register_document_features_with_X_factory(X_factory, 0, term_freq)
		return X_factory.get_csr_matrix()

	def _augment_term_freq_with_unigrams_and_bigrams(self, bigrams, term_freq, term_idx_store, unigrams):
		for term in unigrams + bigrams:
			if term in term_idx_store:
				term_freq[term_idx_store.getidx(term)] += 1


def build_from_category_whitespace_delimited_text(category_text_iter):
	'''

	Parameters
	----------
	category_text_iter iterator of (string category name, one line per sentence, whitespace-delimited text) pairs

	Returns
	-------
	TermDocMatrix
	'''
	y = []
	X_factory = CSRMatrixFactory()
	term_idx_store = IndexStore()
	category_idx_store = IndexStore()
	mX_factory = CSRMatrixFactory()
	metadata_idx_store = IndexStore()
	for doci, (category, text) in enumerate(category_text_iter):
		y.append(category_idx_store.getidx(category))
		term_freq = Counter()
		for sent in text.strip(string.punctuation).lower().split('\n'):
			unigrams = []
			for tok in sent.strip().split():
				unigrams.append(tok)
			bigrams = list(map(' '.join, zip(unigrams[:-1], unigrams[1:])))
			for term in unigrams + bigrams:
				term_freq[term_idx_store.getidx(term)] += 1
		for word_idx, freq in term_freq.items():
			X_factory[doci, word_idx] = freq
	metadata_idx_store = IndexStore()
	return TermDocMatrix(X=X_factory.get_csr_matrix(),
	                     mX=mX_factory.get_csr_matrix(),
	                     y=np.array(y),
	                     term_idx_store=term_idx_store,
	                     metadata_idx_store=metadata_idx_store,
	                     category_idx_store=category_idx_store)
