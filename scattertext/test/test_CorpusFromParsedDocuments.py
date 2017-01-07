import json
import os
import pkgutil
import re
from unittest import TestCase

import pandas as pd
import numpy as np

from scattertext import fast_but_crap_nlp, CorpusFromParsedDocuments, ParsedCorpus
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory
from scattertext.test.test_TermDocMat import get_hamlet_docs, get_hamlet_snippet_binary_category
from scattertext.test.test_corpusFromPandas import get_docs_categories


def clean_function_factory():
	only_speaker_text_re = re.compile(
		r'((^|\n)((ANNOUNCER|AUDIENCE MEMBERS?): .+)($|\n)|(\n|^)((([A-Z\.()\- ]+): ))|\(.+\) *)',
		re.M)
	assert only_speaker_text_re.sub('', 'AUDIENCE MEMBERS: (Chanting.) USA! USA! USA! USA!') == ''
	assert only_speaker_text_re.sub('', 'AUDIENCE MEMBER: (Chanting.) USA! USA! USA! USA!') == ''
	assert only_speaker_text_re.sub('', 'ANNOUNCER: (Chanting.) USA! USA! USA! USA!') == ''
	assert only_speaker_text_re.sub('', 'TOM SMITH: (Chanting.) USA! USA! USA! USA!') == 'USA! USA! USA! USA!'
	assert only_speaker_text_re.sub('', 'DONALD TRUMP: blah blah blah!') == 'blah blah blah!'
	assert only_speaker_text_re.sub('', 'HILLARY CLINTON: (something parenthetical) blah blah blah!') == 'blah blah blah!'
	assert only_speaker_text_re.sub \
		       ('',
		        'ANNOUNCER: (Chanting.) USA! USA! USA! USA!\nTOM SMITH: (Chanting.) ONLY INCLUDE THIS! ONLY KEEP THIS! \nAUDIENCE MEMBER: (Chanting.) USA! USA! USA! USA!').strip() \
	       == 'ONLY INCLUDE THIS! ONLY KEEP THIS!'

	def clean_document(text):
		return only_speaker_text_re.sub('', text)

	return clean_document


def convention_speech_iter():
	relative_path = os.path.join('../scattertext/data', 'political_data.json')
	try:
		cwd = os.path.dirname(os.path.abspath(__file__))
		path = os.path.join(cwd, relative_path)
		return json.load(open(path))
	except:
		return json.loads(pkgutil.get_data('scattertext', relative_path).decode('utf-8'))


def iter_party_speech_pairs():
	for speaker_obj in convention_speech_iter():
		political_party = speaker_obj['name']
		for speech in speaker_obj['speeches']:
			yield political_party, speech


def build_term_doc_matrix():
	term_doc_matrix = TermDocMatrixFactory(
		category_text_iter=iter_party_speech_pairs(),
		clean_function=clean_function_factory(),
		nlp=fast_but_crap_nlp
	).build()
	return term_doc_matrix


class TestCorpusFromParsedDocuments(TestCase):
	@classmethod
	def setUp(cls):
		cls.categories, cls.documents = get_docs_categories()
		cls.parsed_docs = []
		for doc in cls.documents:
			cls.parsed_docs.append(fast_but_crap_nlp(doc))
		cls.df = pd.DataFrame({'category': cls.categories,
		                       'parsed': cls.parsed_docs})
		cls.corpus_fact = CorpusFromParsedDocuments(cls.df, 'category', 'parsed')

	def test_same_as_term_doc_matrix(self):
		term_doc_matrix = build_term_doc_matrix()
		corpus = self._make_political_corpus()

		self.assertEqual(term_doc_matrix._X.shape, corpus._X.shape)
		self.assertEqual((corpus._X != term_doc_matrix._X).nnz, 0)
		corpus_scores = corpus.get_scaled_f_scores('democrat')
		term_doc_matrix_scores = corpus.get_scaled_f_scores('democrat')
		self.assertTrue(np.array_equal(term_doc_matrix_scores, corpus_scores))

	def _make_political_corpus(self):
		clean = clean_function_factory()
		data = []
		for party, speech in iter_party_speech_pairs():
			cleaned_speech = clean(speech)
			if cleaned_speech and cleaned_speech != '':
				parsed_speech = fast_but_crap_nlp(cleaned_speech)
				data.append({'party': party,
				             'text': parsed_speech})
		corpus = CorpusFromParsedDocuments(pd.DataFrame(data),
		                                   category_col='party',
		                                   parsed_col='text').build()
		return corpus

	def test_get_y_and_populate_category_idx_store(self):
		self.corpus_fact.build()
		self.assertEqual([0, 0, 0, 0, 1, 1, 1, 1, 1, 2], list(self.corpus_fact.y))
		self.assertEqual([(0, 'hamlet'), (1, 'jay-z/r. kelly'), (2, '???')],
		                 list(sorted(list(self.corpus_fact._category_idx_store.items()))))

	def test_get_term_idx_and_x(self):
		docs = [fast_but_crap_nlp('aa aa bb.'),
		        fast_but_crap_nlp('bb aa a.')]
		df = pd.DataFrame({'category': ['a', 'b'],
		                   'parsed': docs})
		corpus_fact = CorpusFromParsedDocuments(df, 'category', 'parsed')
		corpus = corpus_fact.build()
		self.assertEqual(list(corpus_fact._term_idx_store.items()),
		                 [(0, 'aa'), (1, 'aa aa'), (2, 'bb'), (3, 'aa bb'), (4, 'a'),
		                  (5, 'bb aa'), (6, 'aa a')]
		                 )
		self.assertEqual(list(sorted(corpus_fact.X.todok().items())),
		                 [((0, 0), 2), ((0, 1), 1), ((0, 2), 1), ((0, 3), 1),
		                  ((1, 0), 1), ((1, 2), 1), ((1, 4), 1), ((1, 5), 1), ((1, 6), 1)]
		                 )
		self.assertTrue(isinstance(corpus, ParsedCorpus))

	def test_hamlet(self):
		raw_docs = get_hamlet_docs()
		categories = [get_hamlet_snippet_binary_category(doc) for doc in raw_docs]
		docs = [fast_but_crap_nlp(doc) for doc in raw_docs]
		df = pd.DataFrame({'category': categories,
		                   'parsed': docs})
		corpus_fact = CorpusFromParsedDocuments(df, 'category', 'parsed')
		corpus = corpus_fact.build()
		tdf = corpus.get_term_freq_df()
		self.assertEqual(list(tdf.ix['play']), [37, 5])
		self.assertFalse(any(corpus.search('play').apply(lambda x: 'plfay' in str(x['parsed']), axis=1)))
		self.assertTrue(all(corpus.search('play').apply(lambda x: 'play' in str(x['parsed']), axis=1)))

		# !!! to do verify term doc matrix
		play_term_idx = corpus_fact._term_idx_store.getidx('play')
		play_X = corpus_fact.X.todok()[:, play_term_idx]

		self.assertEqual(play_X.sum(), 37 + 5)
