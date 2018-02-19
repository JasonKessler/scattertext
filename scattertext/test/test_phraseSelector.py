from unittest import TestCase

from scattertext.termcompaction.PhraseSelector import PhraseSelector
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_term_doc_mat


class TestPhraseSelector(TestCase):
	def test_compact(self):
		tdm = build_hamlet_jz_term_doc_mat()
		c = PhraseSelector(minimum_pmi=10).compact(tdm)
		bigrams = [t for t in tdm.get_terms() if ' ' in t]
		new_bigrams = [t for t in c.get_terms() if ' ' in t]
		self.assertLess(len(new_bigrams), len(bigrams))
		self.assertTrue(set(new_bigrams) -set(bigrams) == set())
