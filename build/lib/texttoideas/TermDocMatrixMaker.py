import spacy

from scattertext.TermDocMatrixFactory import build_from_category_spacy_doc_iter


class TermDocMatrixMaker:
	def __init__(self,
	             category_iter = None,
	             text_iter = None,
	             clean_function = lambda x: x,
	             nlp = None
	             ):
		"""Class for easy construction of a term document matrix.
		   This class let's you define an iterator for each document (text_iter),
		   an iterator for each document's category name (category_iter),
		   and a document cleaning function that's applied to each document
		   before it's parsed.

		   Parameters
		   ----------
		   clean_function : function
		       function that takes a unicode document and returns
		       a cleaned version of that document
		   text_iter : iter<unicode>
		       an iterator that iterates through the unicode text of each
		        document
		   category_iter : iter<str>
		       an iterator the same size as text iter that gives a string or
		       unicode name of each document catgory.  Defaults to the
		       identity function
		    nlp : spacy.en.English
		       the spaCy parser used to parse documents.  If it's None,
		       the class will go through the expensive operation of
		       creating one to parse the text
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
		    tet_iter = documents,
		    clean_function = clean_functions
		   )
		   >>> clf.fit([[0,0], [1, 1], [2, 2]], [0, 1, 2])
		   >>> clf.predict([[1, 1]])
		   array([ 1.])
		   Notes
		   --------
		   See examples/linear_model/plot_ard.py for an example.
		"""
		self._category_iter = category_iter
		self._text_iter = text_iter
		self._clean_function = clean_function
		self._nlp = None

	def get_term_doc_matrix(self):
		nlp = self._nlp
		if nlp is None:
			nlp = spacy.en.English()

		category_document_iter = (
			(category, self._clean_function(raw_text))
			for category, raw_text
			in zip(self._category_iter, self._text_iter)
		)
		term_doc_matrix = build_from_category_spacy_doc_iter(
			category_doc_iter=(
				(category, nlp(text))
				for (category, text)
				in category_document_iter
				if text.strip() != ''
			)
		)







