from collections import Counter
from re import split
from sys import version_info

import pandas as pd

from scattertext.Common import GENERAL_INQUIRER_URL
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromGeneralInquirer(FeatsFromSpacyDoc):
	def __init__(self,
	             use_lemmas=False,
	             entity_types_to_censor=set(),
	             tag_types_to_censor=set(),
	             strip_final_period=False,
	             **kwargs):
		'''
		Parameters
		----------
		empath_analyze_function: function (default=empath.Empath().analyze)
			Function that produces a dictionary mapping Empath categories to

		Other parameters from FeatsFromSpacyDoc.__init__
		'''
		self._lexicon_df = self._download_and_parse_general_inquirer()
		super(FeatsFromGeneralInquirer, self).__init__(use_lemmas,
		                                                entity_types_to_censor,
		                                                tag_types_to_censor,
		                                                strip_final_period)

	def _download_and_parse_general_inquirer(self):
		df = pd.read_csv(GENERAL_INQUIRER_URL, sep='\t')
		return (df.T[2:-4].apply(lambda x: list(df
		                                        .Entry
		                                        .apply(lambda x: x.split('#')[0])
		                                        .loc[x.dropna().index]
		                                        .drop_duplicates()
		                                        .apply(str.lower)),
		                         axis=1)
			.apply(pd.Series)
			.stack()
			.reset_index()[['level_0', 0]]
			.rename(columns={'level_0': 'cat', 0: 'term'})
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
		empath_counter = Counter()
		if version_info[0] >= 3:
			doc = str(doc)
		for empath_category, score in self._analyze(doc).to_dict()[0].items():
			empath_counter[prefix + empath_category] = int(score)
		return empath_counter
