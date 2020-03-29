from collections import Counter

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class UseFullDocAsFeature(FeatsFromSpacyDoc):
    def get_feats(self, doc):
        '''
        Parameters
        ----------
        doc, Spacy Docs

        Returns
        -------
        Counter str -> count
        '''
        return Counter({str(doc):1})
