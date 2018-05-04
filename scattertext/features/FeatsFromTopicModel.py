from collections import Counter
from re import split
from sys import version_info

import pandas as pd

from scattertext.ScatterChart import check_topic_model_string_format
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromTopicModel(FeatsFromSpacyDoc):
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

	def _get_lexicon_df_from_topic_model(self, topic_model):
		return (pd.DataFrame(pd.Series(topic_model)
		                     .apply(pd.Series)
		                     .reset_index())
		        .melt(id_vars=['index'])
		        [['index', 'value']]
		        .rename(columns={'index': 'cat', 'value': 'term'})
		        .set_index('term'))

	def _analyze(self, doc):
		text_df = (pd.DataFrame(pd.Series(Counter(t for t in split(r"(\W)", doc.lower()) if t.strip())))
		           .join(self._lexicon_df)
		           .dropna()
		           .groupby('cat')
		           .sum()
		           )
		return text_df

	def get_doc_metadata(self, doc, prefix=''):
		feature_counter = Counter()
		if version_info[0] >= 3:
			doc = str(doc)
		for category, score in self._analyze(doc).to_dict()[0].items():
			feature_counter[prefix + category] = int(score)
		return feature_counter

	def has_metadata_term_list(self):
		return True

	def get_top_model_term_lists(self):
		return self._topic_model
