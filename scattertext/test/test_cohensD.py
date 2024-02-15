from unittest import TestCase
import numpy as np
from scattertext import OncePerDocFrequencyRanker
from scattertext.termscoring.CohensD import CohensD, HedgesG
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus_with_meta, build_hamlet_jz_corpus


class TestCohensD(TestCase):
    def test_get_cohens_d_scores(self):
        corpus = build_hamlet_jz_corpus()
        np.testing.assert_almost_equal(CohensD(corpus)
                                       .set_term_ranker(OncePerDocFrequencyRanker)
                                       .set_categories('hamlet')
                                       .get_scores()[:5], [-0.2303607, 0.8838835, 0.8838835, 1.4028612, 0.8838835])

    def test_get_cohens_d_scores_zero_robust(self):
        corpus = build_hamlet_jz_corpus()
        corpus._X[1, :] = 0
        np.testing.assert_almost_equal(CohensD(corpus)
                                       .set_term_ranker(OncePerDocFrequencyRanker)
                                       .set_categories('hamlet')
                                       .get_scores()[:5], [-0.2303607, 0.8838835, 0.8838835, 0.8838835, 0.8838835])

    def test_get_cohens_d_score_df(self):
        corpus = build_hamlet_jz_corpus()
        columns = (CohensD(corpus)
                   .set_term_ranker(OncePerDocFrequencyRanker)
                   .set_categories('hamlet')
                   .get_score_df().columns)
        self.assertEqual(set(columns), set(['cohens_d', 'cohens_d_se', 'cohens_d_z', 'cohens_d_p', 'hedges_g',
                                            'hedges_g_se', 'hedges_g_z', 'hedges_g_p', 'm1', 'm2',
                                            'count1', 'count2', 'docs1', 'docs2']))

    def test_get_cohens_d_score_df_p_vals(self):
        corpus = build_hamlet_jz_corpus()
        columns = (CohensD(corpus)
                   .set_term_ranker(OncePerDocFrequencyRanker)
                   .set_categories('hamlet')
                   .get_score_df().columns)
        self.assertEqual(set(columns), set(['cohens_d', 'cohens_d_se', 'cohens_d_z', 'cohens_d_p', 'hedges_g',
                                            'hedges_g_se', 'hedges_g_z', 'hedges_g_p', 'm1', 'm2',
                                            'count1', 'count2', 'docs1', 'docs2']))

    def test_get_name(self):
        corpus = build_hamlet_jz_corpus()
        self.assertEqual(CohensD(corpus)
                         .set_categories('hamlet')
                         .get_name(),
                         "Cohen's d")

    def test_get_name_hedges(self):
        corpus = build_hamlet_jz_corpus()
        self.assertEqual(HedgesG(corpus).set_categories('hamlet').get_name(), "Hedge's g")
        self.assertEqual(len(HedgesG(corpus).set_categories('hamlet').get_scores()), corpus.get_num_terms())
