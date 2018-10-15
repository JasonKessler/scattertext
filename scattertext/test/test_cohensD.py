from unittest import TestCase
import numpy as np
from scattertext import OncePerDocFrequencyRanker
from scattertext.termscoring.CohensD import CohensD
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus_with_meta, build_hamlet_jz_corpus


class TestCohensD(TestCase):
    def test_get_cohens_d_scores(self):
        corpus = build_hamlet_jz_corpus()
        np.testing.assert_almost_equal(CohensD(corpus)
                                       .set_term_ranker(OncePerDocFrequencyRanker)
                                       .set_categories('hamlet')
                                       .get_cohens_d_scores()[:9], [0., 0.8242361, 0.8242361, 1.4276187, 0.8242361,
                                                                0.8242361, 0.8242361, 0.8242361, 0.5395892])

    def test_get_scores(self):
        corpus = build_hamlet_jz_corpus()
        np.testing.assert_almost_equal(CohensD(corpus)
                                       .set_term_ranker(OncePerDocFrequencyRanker)
                                       .set_categories('hamlet')
                                       .get_scores()[:9], [0., 0.8242361, 0.8242361, 1.4276187, 0.8242361,
                                                                    0.8242361, 0.8242361, 0.8242361, 0.5395892])

    def test_get_name(self):
        corpus = build_hamlet_jz_corpus()
        self.assertEqual(CohensD(corpus)
                         .set_categories('hamlet')
                         .get_name(),
                         "Cohen's d")
