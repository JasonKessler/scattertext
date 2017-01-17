from unittest import TestCase

import pandas as pd

from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext import TermDocMatrixFromPandas
from scattertext.test.test_termDocMatrixFactory import get_docs_categories


class TestTermDocMatrixFromPandas(TestCase):
	def test_main(self):
		categories, documents = get_docs_categories()
		df = pd.DataFrame({'category': categories,
		                   'text': documents})
		tdm_factory = TermDocMatrixFromPandas(df,
		                                      'category',
		                                      'text',
		                                      nlp=whitespace_nlp)
		term_doc_matrix = tdm_factory.build()
		self.assertIsInstance(term_doc_matrix, TermDocMatrix)
		self.assertEqual(set(term_doc_matrix.get_categories()),
		                 set(['hamlet','jay-z/r. kelly']))
		self.assertEqual(term_doc_matrix.get_num_docs(), 9)
		term_doc_df = term_doc_matrix.get_term_freq_df()
		self.assertEqual(term_doc_df.ix['of'].sum(), 3)
