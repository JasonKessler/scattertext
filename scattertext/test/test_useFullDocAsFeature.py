from collections import Counter
from unittest import TestCase

from scattertext import whitespace_nlp_with_sentences
from scattertext.features.UseFullDocAsFeature import UseFullDocAsFeature


class TestUseFullDocAsFeature(TestCase):
    def test_get_feats(self):
        doc = whitespace_nlp_with_sentences("A a bb cc.")
        term_freq = UseFullDocAsFeature().get_feats(doc)
        self.assertEqual(Counter({"A a bb cc.": 1}), term_freq)

