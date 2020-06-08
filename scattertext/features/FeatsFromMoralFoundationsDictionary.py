import io
import pkgutil
from collections import Counter
from re import split
from sys import version_info

import pandas as pd

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromMoralFoundationsDictionary(FeatsFromSpacyDoc):
    def __init__(self,
                 use_lemmas=False,
                 entity_types_to_censor=set(),
                 tag_types_to_censor=set(),
                 strip_final_period=False,
                 **kwargs):
        '''
        Parameters
        ----------
        Other parameters from FeatsFromSpacyDoc.__init__
        '''
        self._lexicon_df = self._load_mfd()
        super(FeatsFromMoralFoundationsDictionary, self).__init__(use_lemmas,
                                                                  entity_types_to_censor,
                                                                  tag_types_to_censor,
                                                                  strip_final_period)

    def _load_mfd(self):
        return pd.read_csv(
            io.StringIO(pkgutil.get_data('scattertext', 'data/mfd2.0.csv').decode('utf-8'))
        ).set_index('term')

    def _analyze(self, doc):
        text_df = (pd.DataFrame(pd.Series(Counter(t for t in split(r"(\W)", doc.lower()) if t.strip())))
                   .join(self._lexicon_df)
                   .dropna()
                   .groupby('cat')
                   .sum()
                   )
        return text_df

    def get_definitions(self):
        '''
        These definitions are from https://osf.io/xakyw/

        :return: dict
        '''
        return {
            'care.virtue': '...acted with kindness, compassion, or empathy, or nurtured another person.',
            'care.vice': '...acted with cruelty, or hurt or harmed another person/animal and caused suffering.',
            'fairness.virtue': '...acted in a fair manner, promoting equality, justice, or rights.',
            'fairness.vice': '...was unfair or cheated, or caused an injustice or engaged in fraud.',
            'loyalty.virtue': '...acted with fidelity, or as a team player, or was loyal or patriotic.',
            'loyalty.vice': '...acted disloyal, betrayed someone, was disloyal, or was a traitor.',
            'authority.virtue': '...obeyed, or acted with respect for authority or tradition.',
            'authority.vice': '...disobeyed or showed disrespect, or engaged in subversion or caused chaos',
            'sanctity.virtue': '...acted in a way that was wholesome or sacred, or displayed purity or sanctity',
            'sanctity.vice': '...was depraved, degrading, impure, or unnatural.'
        }

    def get_doc_metadata(self, doc, prefix=''):
        topic_counter = Counter()
        if version_info[0] >= 3:
            doc = str(doc)
        for topic_category, score in self._analyze(doc).to_dict()[0].items():
            topic_counter[prefix + topic_category] = int(score)
        return topic_counter

    def has_metadata_term_list(self):
        return True

    def get_top_model_term_lists(self):
        return self._lexicon_df.reset_index().groupby('cat')['term'].apply(list).to_dict()
