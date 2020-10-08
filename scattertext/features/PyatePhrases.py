from collections import Counter
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class PyatePhrases(FeatsFromSpacyDoc):
    def __init__(self, extractor=None, **args):
        import pyate
        self._extractor = pyate.combo_basic if extractor is None else extractor
        FeatsFromSpacyDoc.__init__(self, **args)

    def get_feats(self, doc):
        return Counter(self._extractor(str(doc)).to_dict())

