import re
from unittest import TestCase

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import PassiveAggressiveClassifier

from scattertext import TermDocMatrixFactory
from scattertext.FastButCrapNLP import fast_but_crap_nlp, Doc, Tok
from scattertext.TermDocMatrixFactory import FeatsFromDoc


def build_hamlet_jz_term_doc_mat():
	categories, documents = get_docs_categories()
	clean_function = lambda text: '' if text.startswith('[') else text
	term_doc_mat = TermDocMatrixFactory(
		category_text_iter=zip(categories, documents),
		clean_function=clean_function,
		nlp=fast_but_crap_nlp
	).build()
	return term_doc_mat


def get_docs_categories():
	documents = [u"What art thou that usurp'st this time of night,",
	             u'Together with that fair and warlike form',
	             u'In which the majesty of buried Denmark',
	             u'Did sometimes march? by heaven I charge thee, speak!',
	             u'Halt! Who goes there?',
	             u'[Intro]',
	             u'It is I sire Tone from Brooklyn.',
	             u'Well, speak up man what is it?',
	             u'News from the East sire! THE BEST OF BOTH WORLDS HAS RETURNED!'
	             ]
	categories = ['hamlet'] * 4 + ['jay-z/r. kelly'] * 5
	return categories, documents


def _testing_nlp(doc):
	toks = []
	for tok in re.split(r"(\W)", doc):
		pos = 'WORD'
		ent = ''
		if tok.strip() == '':
			pos = 'SPACE'
		elif re.match('^\W+$', tok):
			pos = 'PUNCT'
		if tok == 'Tone':
			ent = 'PERSON'
		if tok == 'Brooklyn':
			ent = 'GPE'
		toks.append(Tok(pos, tok[:2].lower(), tok.lower(), ent))
	return Doc([toks])


class TestTermDocMatrixFactory(TestCase):
	def test_build(self):
		term_doc_mat = build_hamlet_jz_term_doc_mat()
		self.assertEqual(term_doc_mat.get_num_docs(), 8)
		self.assertEqual(term_doc_mat.get_categories(), ['hamlet', 'jay-z/r. kelly'])

	def test_build_censor_entities(self):
		categories, documents = get_docs_categories()
		clean_function = lambda text: '' if text.startswith('[') else text
		term_doc_mat = (
			TermDocMatrixFactory(
				category_text_iter=zip(categories, documents),
				clean_function=clean_function,
				nlp=_testing_nlp
			)
				.censor_entity_types(set(['GPE']))
				.build()
		)
		self.assertIn('GPE', set(term_doc_mat.get_term_freq_df().index))
		self.assertNotIn('brooklyn', set(term_doc_mat.get_term_freq_df().index))

class TestFeatsFromDoc(TestCase):
	def test_main(self):
		categories, documents = get_docs_categories()
		clean_function = lambda text: '' if text.startswith('[') else text
		entity_types = set(['GPE'])
		term_doc_mat = (
			TermDocMatrixFactory(
				category_text_iter=zip(categories, documents),
				clean_function=clean_function,
				nlp=_testing_nlp
			)
				.censor_entity_types(entity_types)
				.build()
		)
		clf = PassiveAggressiveClassifier(n_iter=5, C=0.5, n_jobs=-1, random_state=0)
		fdc = FeatsFromDoc(term_doc_mat._term_idx_store, clean_function=clean_function, entity_types=entity_types).set_nlp(_testing_nlp)
		tfidf = TfidfTransformer(norm='l1')
		X = tfidf.fit_transform(term_doc_mat._X)
		clf.fit(X, term_doc_mat._y)
		X_to_predict = fdc.feats_from_doc('Did sometimes march UNKNOWNWORD')
		pred = clf.predict(tfidf.transform(X_to_predict))
		dec = clf.decision_function(X_to_predict)


