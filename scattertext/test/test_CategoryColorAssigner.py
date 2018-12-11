from unittest import TestCase

import pandas as pd

from scattertext import CorpusFromPandas, CSRMatrixFactory, IndexStore
from scattertext import whitespace_nlp
from scattertext.CategoryColorAssigner import CategoryColorAssigner
from scattertext.test.test_corpusFromPandas import get_docs_categories


class TestCategoryColorAssigner(TestCase):
    def test_main(self):
        categories, documents = get_docs_categories()
        df = pd.DataFrame({'category': categories, 'text': documents})
        corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
        self.assertEqual(CategoryColorAssigner(corpus).get_category_colors().to_dict(),
                         {'???': [255, 127, 14],
                          'hamlet': [174, 199, 232],
                          'jay-z/r. kelly': [31, 119, 180]})
        term_colors = CategoryColorAssigner(corpus).get_term_colors()
        self.assertEqual(term_colors['this time'], 'aec7e8')
        self.assertEqual(term_colors['sire'], '1f77b4')
        self.assertEqual(len(term_colors), corpus.get_num_terms())
        mfact = CSRMatrixFactory()
        mis = IndexStore()
        for i, c in enumerate(df['category']):
            mfact[i, mis.getidx(c)] = 1
        corpus = corpus.add_metadata(mfact.get_csr_matrix(), mis)
        meta_colors = CategoryColorAssigner(corpus, use_non_text_features=True).get_term_colors()
        self.assertEqual(meta_colors, {'hamlet': 'aec7e8', 'jay-z/r. kelly': '1f77b4', '???': 'ff7f0e'})
        self.assertNotEqual(CategoryColorAssigner(corpus).get_term_colors(), meta_colors)
