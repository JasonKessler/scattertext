from unittest import TestCase

import numpy as np

from scattertext import CohensD, CredTFIDF, OncePerDocFrequencyRanker
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestCredTFIDF(TestCase):
    def test_get_score_df(self):
        corpus = build_hamlet_jz_corpus()
        tfidf = (CredTFIDF(corpus)
                 .set_term_ranker(OncePerDocFrequencyRanker)
                 .set_categories('hamlet'))

        np.testing.assert_almost_equal(tfidf
                                       .get_scores()[:5], [3.0757237e-05, 4.1256023e-02, 4.1256023e-02, 5.5708409e-02,
                                                           4.1256023e-02])
        #print(tfidf.get_score_df().iloc[0])
        self.assertEqual(list(tfidf.get_score_df().columns), ['pos_cred_tfidf', 'neg_cred_tfidf', 'delta_cred_tf_idf'])


    def test_get_name(self):
        corpus = build_hamlet_jz_corpus()
        self.assertEqual(CredTFIDF(corpus).get_name(), 'Delta mean cred-tf-idf')
