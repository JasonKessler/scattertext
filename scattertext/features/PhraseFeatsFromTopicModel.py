from collections import Counter
from functools import reduce

from scattertext import FeatsFromSpacyDoc
from scattertext.features.FeatsFromTopicModel import FeatsFromTopicModelBase


class PhraseFeatsFromTopicModel(FeatsFromTopicModelBase, FeatsFromSpacyDoc):
    '''
    This class allows you to make use of a topic model which has multi-token entries (i.e., terms in topics which
    have spaces in them.)
    It requires Flashtext to be installed.
    '''
    def __init__(self,
                 topic_model,
                 use_lemmas=False,
                 entity_types_to_censor=set(),
                 entity_types_to_use=None,
                 tag_types_to_censor=set(),
                 strip_final_period=False,
                 keyword_processor_args = {'case_sensitive' :False}):
        from flashtext import KeywordProcessor
        self._keyword_processor = KeywordProcessor(**keyword_processor_args)
        self._topic_model = topic_model
        for keyphrase in reduce(lambda x, y: set(x) | set(y), topic_model.values()):
            self._keyword_processor.add_keyword(keyphrase)
        FeatsFromSpacyDoc.__init__(self, use_lemmas, entity_types_to_censor,
                                   tag_types_to_censor, strip_final_period)
        FeatsFromTopicModelBase.__init__(self, topic_model)


    def get_top_model_term_lists(self):
        return self._topic_model

    def _get_terms_from_doc(self, doc):
        return Counter(self._keyword_processor.extract_keywords(doc))

    def get_feats(self, doc):
        return Counter(self._get_terms_from_doc(str(doc)))