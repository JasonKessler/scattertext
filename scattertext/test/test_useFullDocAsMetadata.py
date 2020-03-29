from collections import Counter
from unittest import TestCase

from scattertext import whitespace_nlp_with_sentences
from scattertext.features.UseFullDocAsMetadata import UseFullDocAsMetadata


class TestUseFullDocAsMetadata(TestCase):
    def test_get_feats(self):
        doc = whitespace_nlp_with_sentences("A a bb cc.")
        term_freq = UseFullDocAsMetadata().get_doc_metadata(doc)
        self.assertEqual(Counter({"A a bb cc.": 1}), term_freq)

