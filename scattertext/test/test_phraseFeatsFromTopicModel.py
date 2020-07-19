from collections import Counter
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock
import sys

from scattertext.features.PhraseFeatsFromTopicModel import PhraseFeatsFromTopicModel


class TestPhraseFeatsFromTopicModel(TestCase):
    def test_get_doc_get_feats(self):
        flashtext = MagicMock()
        flashtext.KeywordProcessor().extract_keywords.return_value = ['A b', 'A b', 'C e F', 'B']
        sys.modules["flashtext"] = flashtext

        expected = Counter({'A b': 2, 'C e F': 1, 'B': 1})

        actual = PhraseFeatsFromTopicModel(
            topic_model={'Topic A': ['A b', 'b', 'C e F'],
                         'Topic B': ['B', 'C e F']}
        ).get_feats('A b A b C e F B')

        self.assertEqual(expected, actual)


    def test_get_doc_metadata(self):
        flashtext = MagicMock()
        flashtext.KeywordProcessor().extract_keywords.return_value = ['A b', 'A b', 'C e F', 'B']
        sys.modules["flashtext"] = flashtext

        expected = Counter({'Topic A': 3, 'Topic B': 2})

        actual = PhraseFeatsFromTopicModel(
            topic_model={'Topic A': ['A b', 'b', 'C e F'],
                         'Topic B': ['B', 'C e F']}
        ).get_doc_metadata('A b A b C e F B')

        self.assertEqual(expected, actual)
