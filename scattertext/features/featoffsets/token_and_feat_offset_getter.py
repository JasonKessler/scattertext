from typing import List

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter


class TokenFeatAndOffsetGetter(FeatAndOffsetGetter):
    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(self, doc):
        offset_tokens = {}
        for sent in doc.sents:
            for tok in sent:
                token_stats = offset_tokens.setdefault(tok.lower_, [0, []])
                token_stats[0] += 1
                token_stats[1].append((tok.idx, tok.idx + len(tok.lower_)))
        return offset_tokens.items()


class POSFeatures(FeatAndOffsetGetter):
    def __init__(self, allowable_pos_tags: List[str]):
        self.allowable_pos_tags = allowable_pos_tags

    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(self, doc):
        offset_tokens = {}
        for sent in doc.sents:
            for tok in sent:
                if tok.tag_ in self.allowable_pos_tags:
                    token_stats = offset_tokens.setdefault(tok.lower_, [0, []])
                    token_stats[0] += 1
                    token_stats[1].append((tok.idx, tok.idx + len(tok.lower_)))
        return offset_tokens.items()