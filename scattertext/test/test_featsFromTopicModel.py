from collections import Counter
from unittest import TestCase

from scattertext.features.FeatsFromTopicModel import FeatsFromTopicModel


class TestFeatsFromTopicModel(TestCase):
    def test_get_doc_get_feats(self):
        expected = Counter({'A b': 2, 'C e F': 1, 'b': 1})

        actual = FeatsFromTopicModel(
            topic_model={'Topic A': ['A b', 'b', 'C e F'],
                         'Topic B': ['B', 'C e F']}
        ).get_feats('A b A b C e F B')

        self.assertEqual(expected, actual)


    def test_get_doc_metadata(self):
        expected = Counter({'Topic A': 3, 'Topic B': 2})

        actual = FeatsFromTopicModel(
            topic_model={'Topic A': ['A b', 'b', 'C e F'],
                         'Topic B': ['B', 'C e F']},
            keyword_processor_args={'case_sensitive': True}
        ).get_doc_metadata('A b A b C e F B')

        self.assertEqual(expected, actual)
