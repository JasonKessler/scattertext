import unittest
import pandas as pd
from scattertext.WhitespaceNLP import whitespace_nlp

from scattertext import CorpusWithoutCategoriesFromParsedDocuments


class TestCorpusWithoutCategoriesFromParsedDocuments(unittest.TestCase):
    def test_main(self):
        doc_df = pd.DataFrame({
            'Text': [x.strip() for x in '''b a m n i b e u p
        b a s a t b e w q n
        b c a g a b e s t a
        b a g h a b e a a t
        b a h a a b e a x a t'''.split('\n')]}).assign(
            Parse=lambda df: df.Text.apply(whitespace_nlp)
        )
        corpus = CorpusWithoutCategoriesFromParsedDocuments(doc_df, parsed_col='Parse').build()
