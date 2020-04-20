from collections import Counter

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class UseFullDocAsMetadata(FeatsFromSpacyDoc):
    def get_feats(self, doc):
        return Counter()

    def get_doc_metadata(self, doc):
        '''
        Parameters
        ----------
        doc, Spacy Docs

        Returns
        -------
        Counter str -> count
        '''
        return Counter({str(doc): 1})
