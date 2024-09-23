from collections import Counter

from cytoolz.itertoolz import sliding_window

from scattertext import FeatsFromSpacyDoc


class FeatsFromSpacyDocMultiGrams(FeatsFromSpacyDoc):
    def __init__(self, ngrams, pos_as_tag=None):
        super(FeatsFromSpacyDocMultiGrams, self).__init__()
        self.pos_as_tag = pos_as_tag
        self.ngrams = ngrams

    def get_feats(self, doc):
        ngrams_counter = Counter()
        for sent in doc.sents:
            words = self._get_unigram_feats(sent)
            for ngrams in self._get_ngram_feats(words):
                ngrams_counter += Counter(ngrams)
        return ngrams_counter

    def _get_ngram_feats(self, words):
        for ngram in self.ngrams:
            if len(words) >= ngram:
                yield map(' '.join, sliding_window(ngram, words))

    def _get_unigram_feats(self, sent):
        return [
            tok.text.strip() if tok.pos_ not in self.pos_as_tag else tok.pos_
            for tok
            in sent
        ]
