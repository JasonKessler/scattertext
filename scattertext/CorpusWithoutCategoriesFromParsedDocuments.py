import string

import numpy as np
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class CorpusWithoutCategoriesFromParsedDocuments(object):
    def __init__(self,
                 df,
                 parsed_col,
                 feats_from_spacy_doc=FeatsFromSpacyDoc()):

        '''
        Parameters
        ----------
        df : pd.DataFrame
         contains category_col, and parse_col, were parsed col is entirely spacy docs
        parsed_col : str
            name of spacy parsed column in convention_df
        feats_from_spacy_doc : FeatsFromSpacyDoc
        '''
        self.df = df
        self.parsed_col = parsed_col
        self.feats_from_spacy_doc = feats_from_spacy_doc

    def build(self):
        '''

        :return: ParsedCorpus
        '''
        category_col = 'Category'
        while category_col in self.df:
            category_col = 'Category_' + ''.join(np.random.choice(string.ascii_letters) for _ in range(5))
        return CorpusFromParsedDocuments(
            self.df.assign(**{category_col: '_'}),
            category_col,
            self.parsed_col,
            feats_from_spacy_doc=self.feats_from_spacy_doc,
        ).build()