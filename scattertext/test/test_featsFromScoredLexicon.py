from unittest import TestCase
import numpy as np
import pandas as pd

from scattertext import whitespace_nlp_with_sentences
from scattertext.features.FeatsFromScoredLexicon import FeatsFromScoredLexicon


class TestFeatsFromScoredLexicon(TestCase):
    def test_main(self):
        lexicon_df = pd.DataFrame({'activation': {'a': 1.3846,
                                                  'abandon': 2.375,
                                                  'abandoned': 2.1,
                                                  'abandonment': 2.0,
                                                  'abated': 1.3333},
                                   'imagery': {'a': 1.0,
                                               'abandon': 2.4,
                                               'abandoned': 3.0,
                                               'abandonment': 1.4,
                                               'abated': 1.2},
                                   'pleasantness': {'a': 2.0,
                                                    'abandon': 1.0,
                                                    'abandoned': 1.1429,
                                                    'abandonment': 1.0,
                                                    'abated': 1.6667}})

        with self.assertRaises(AssertionError):
            FeatsFromScoredLexicon(3)
        feats_from_scored_lexicon = FeatsFromScoredLexicon(lexicon_df)
        self.assertEqual(set(feats_from_scored_lexicon.get_top_model_term_lists().keys()),
                         set(['activation', 'imagery', 'pleasantness']))
        features = feats_from_scored_lexicon.get_doc_metadata(whitespace_nlp_with_sentences('I abandoned a wallet.'))
        np.testing.assert_almost_equal(features[['activation', 'imagery', 'pleasantness']],
                                       np.array([1.74230, 2.00000, 1.57145]))
