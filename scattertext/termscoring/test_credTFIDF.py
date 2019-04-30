from unittest import TestCase

import numpy as np

from scattertext.termscoring.CredTFIDF import CredTFIDF
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus


class TestCredTFIDF(TestCase):
    def test_get_score_df(self):
        corpus = build_hamlet_jz_corpus()

        self.assertEqual(
            set(CredTFIDF(corpus).set_categories('hamlet').get_score_df().columns),
            set(['pos_cred_tfidf', 'neg_cred_tfidf', 'delta_cred_tf_idf'])
        )
        #print(CredTFIDF(corpus).set_categories('hamlet').get_score_df(bootstrap=True, num_bootstraps=2))

