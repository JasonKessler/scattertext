from abc import ABC, abstractmethod
from collections import Counter
from functools import reduce
from re import split
from sys import version_info

import pandas as pd
from flashtext import KeywordProcessor

from scattertext.ScatterChart import check_topic_model_string_format
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromTopicModelBase(ABC):
    def __init__(self, topic_model):
        self._topic_model = topic_model
        self._lexicon_df = self._get_lexicon_df_from_topic_model(topic_model)

    def _get_lexicon_df_from_topic_model(self, topic_model):
        return (pd.DataFrame(pd.Series(topic_model)
                             .apply(pd.Series)
                             .reset_index())
                .melt(id_vars=['index'])
                [['index', 'value']]
                .rename(columns={'index': 'cat', 'value': 'term'})
                .set_index('term'))

    def _analyze(self, doc):
        text_df = (pd.DataFrame(pd.Series(self._get_terms_from_doc(doc)))
                   .join(self._lexicon_df)
                   .dropna()
                   .groupby('cat')
                   .sum())
        return text_df

    def get_doc_metadata(self, doc, prefix=''):
        feature_counter = Counter()
        if version_info[0] >= 3:
            doc = str(doc)
        for category, score in self._analyze(doc).to_dict()[0].items():
            feature_counter[prefix + category] = int(score)
        return feature_counter

    @abstractmethod
    def _get_terms_from_doc(self, doc):
        pass


class FeatsFromTopicModel(FeatsFromTopicModelBase, FeatsFromSpacyDoc):
    def __init__(self,
                 topic_model,
                 use_lemmas=False,
                 entity_types_to_censor=set(),
                 entity_types_to_use=None,
                 tag_types_to_censor=set(),
                 strip_final_period=False,
                 keyword_processor_args={'case_sensitive': False}):
        self._keyword_processor = KeywordProcessor(**keyword_processor_args)
        self._topic_model = topic_model.copy()
        if keyword_processor_args.get('case_sensitive', None) is False:
            for k, v in self._topic_model.items():
                self._topic_model[k] = [e.lower() for e in v]
        for keyphrase in reduce(lambda x, y: set(x) | set(y), self._topic_model.values()):
            self._keyword_processor.add_keyword(keyphrase)
        FeatsFromSpacyDoc.__init__(self, use_lemmas, entity_types_to_censor,
                                   tag_types_to_censor, strip_final_period)
        FeatsFromTopicModelBase.__init__(self, topic_model)

    def get_top_model_term_lists(self):
        return self._topic_model

    def _get_terms_from_doc(self, doc):
        return Counter(self._keyword_processor.extract_keywords(str(doc)))

    def get_feats(self, doc):
        return Counter(self._get_terms_from_doc(str(doc)))


"""
class FeatsFromTopicModel(FeatsFromSpacyDoc, FeatsFromTopicModelBase):
	def __init__(self,
	             topic_model,
	             use_lemmas=False,
	             entity_types_to_censor=set(),
	             tag_types_to_censor=set(),
	             strip_final_period=False,
	             **kwargs):
		'''
		Parameters
		----------
		topic_model : dict
			{topicmodelname: [term1, term2, ....], ...}

		Other parameters from FeatsFromSpacyDoc.__init__
		'''
		check_topic_model_string_format(topic_model)
		self._topic_model = topic_model
		self._lexicon_df = self._get_lexicon_df_from_topic_model(topic_model)
		super(FeatsFromTopicModel, self).__init__(use_lemmas,
		                                          entity_types_to_censor,
		                                          tag_types_to_censor,
		                                          strip_final_period)




	def _get_terms_from_doc(self, doc):
		return Counter(t for t in split(r"(\W)", doc.lower()) if t.strip())

	def has_metadata_term_list(self):
		return True

	def get_top_model_term_lists(self):
		return self._topic_model
"""
