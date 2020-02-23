from collections import Counter

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class PyTextRankPhrases(FeatsFromSpacyDoc):
    def __init__(self, use_lemmas=False, entity_types_to_censor=set(), tag_types_to_censor=set(),
                 strip_final_period=False):
        FeatsFromSpacyDoc.__init__(self, use_lemmas, entity_types_to_censor, tag_types_to_censor, strip_final_period)
        self._include_chunks = False
        self._rank_smoothing_constant = 0

    def include_chunks(self):
        '''
        Use each chunk in a phrase instead of just the span identified as a phrase
        :return: self
        '''
        self._include_chunks = True
        return self

    def set_rank_smoothing_constant(self, rank_smoothing_constant):
        '''
        Add a quantity

        :param rank_smoothing_constant: float
        :return: self
        '''
        self._rank_smoothing_constant = rank_smoothing_constant
        return self

    def get_doc_metadata(self, doc):
        import pytextrank
        phrase_counter = Counter()
        tr = pytextrank.TextRank()
        tr.doc = doc
        phrases = tr.calc_textrank()
        for phrase in phrases:
            if self._include_chunks:
                for chunk in phrase.chunks:
                    phrase_counter[str(chunk)] += (phrase.rank + self._rank_smoothing_constant)
            else:
                phrase_counter[phrase.text] += phrase.count * (phrase.rank + self._rank_smoothing_constant)
        return phrase_counter

    def get_feats(self, doc):
        return Counter()
