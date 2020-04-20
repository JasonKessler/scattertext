from collections import Counter

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class SpacyEntities(FeatsFromSpacyDoc):
    def __init__(self,
                 use_lemmas=False,
                 entity_types_to_censor=set(),
                 entity_types_to_use=None,
                 tag_types_to_censor=set(),
                 strip_final_period=False):
        self._entity_types_to_use = entity_types_to_use
        FeatsFromSpacyDoc.__init__(self, use_lemmas, entity_types_to_censor,
                                   tag_types_to_censor, strip_final_period)

    def get_feats(self, doc):
        return Counter([
            ' '.join(str(ent).split()).lower()
            for ent
            in doc.ents
            if ((self._entity_types_to_use is None
                 or ent.label_ in self._entity_types_to_use)
                and (ent.label_ not in self._entity_types_to_censor))
        ])
