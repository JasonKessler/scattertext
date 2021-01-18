import unittest
from turtle import st

import pandas as pd
import numpy as np
from scattertext.WhitespaceNLP import whitespace_nlp

from scattertext import Dispersion, CorpusWithoutCategoriesFromParsedDocuments


class TestDispersion(unittest.TestCase):
    def test_main(self):
        doc_df = pd.DataFrame({
            'Text': [x.strip() for x in '''b a m n i b e u p
        b a s a t b e w q n
        b c a g a b e s t a
        b a g h a b e a a t
        b a h a a b e a x a t'''.split('\n')]}).assign(
            Parse=lambda df: df.Text.apply(whitespace_nlp),
        )
        corpus = CorpusWithoutCategoriesFromParsedDocuments(
            doc_df, parsed_col='Parse'
        ).build(
        ).get_unigram_corpus()
        dispersion_df = Dispersion(corpus).get_df()
        dispersion_df = dispersion_df.loc[['b', 'i', 'q', 'x']]
        assert list(dispersion_df['Range'].values) == [5, 1, 1, 1]
        assert list(dispersion_df['SD'].values) == [0, 0.4, 0.4, 0.4]
        assert list(dispersion_df['VC'].values) == [0, 2, 2, 2]
        np.testing.assert_almost_equal(
            list(dispersion_df["Juilland's D"].values),
            np.array([0.968, 0, 0, 0]),
            decimal=3
        )
        np.testing.assert_almost_equal(
            list(dispersion_df["Rosengren's S"].values),
            np.array([0.999, 0.18, 0.2, 0.22]),
            decimal=3

        )
        np.testing.assert_almost_equal(
            list(dispersion_df["DP"].values),
            np.array([0.02, 0.82, 0.8, 0.78]),
            decimal=3
        )
        np.testing.assert_almost_equal(
            list(dispersion_df["DP norm"].values),
            np.array([0.024, 1, 0.976, 0.951]),
            decimal=3
        )
        np.testing.assert_almost_equal(
            list(dispersion_df["KL-divergence"].values),
            np.array([0.003, 2.474, 2.322, 2.184]),
            decimal=3
        )
