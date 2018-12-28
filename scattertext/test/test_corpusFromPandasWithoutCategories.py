
from unittest import TestCase

import numpy as np
import pandas as pd

from scattertext import whitespace_nlp
from scattertext.TermDocMatrixFromPandas import TermDocMatrixWithoutCategoriesFromPandas, TermDocMatrixFromPandas
from scattertext.TermDocMatrixWithoutCategories import TermDocMatrixWithoutCategories
from scattertext.test.test_corpusFromPandas import get_docs_categories

class CorpusFromPandasWithoutCategories():
    pass

def get_term_doc_matrix_without_categories():
    categories, documents = get_docs_categories()
    df = pd.DataFrame({'text': documents})
    tdm = TermDocMatrixWithoutCategoriesFromPandas(df, 'text', nlp=whitespace_nlp).build()
    return tdm


class TestCorpusFromPandasWithoutCategories(TestCase):
    def test_term_category_matrix_from_pandas_without_categories(self):
        tdm = get_term_doc_matrix_without_categories()
        categories, documents = get_docs_categories()
        reg_tdm = TermDocMatrixFromPandas(pd.DataFrame({'text': documents, 'categories': categories}),
                                          text_col='text',
                                          category_col='categories',
                                          nlp=whitespace_nlp).build()

        self.assertIsInstance(tdm, TermDocMatrixWithoutCategories)
        self.assertEqual(tdm.get_terms(), reg_tdm.get_terms())
        self.assertEqual(tdm.get_num_docs(), reg_tdm.get_num_docs())
        np.testing.assert_equal(tdm.get_term_doc_mat().data, reg_tdm.get_term_doc_mat().data)

