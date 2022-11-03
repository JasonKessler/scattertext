from typing import List, Tuple, Union, Optional, Callable
from collections import deque

import spacy.tokens

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter
from scattertext.Common import ENGLISH_STOP_WORDS, MY_ENGLISH_STOP_WORDS


def window(seq, n=2):
    # adapted from https://stackoverflow.com/questions/46516730/how-to-work-with-zip-on-2-generators-s-t-each-returns-the-same-item-that-changes
    it = iter(seq)
    win = deque((next(it, None) for _ in range(n)), maxlen=n)
    yield list(win)
    for e in it:
        win.append(e)
        yield list(win)


class FlexibleNGramFeatures(FeatAndOffsetGetter):
    def __init__(
            self,
            ngram_sizes: Optional[List[int]] = None,
            exclude_ngram_filter: Optional[Callable] = None,
            text_from_token: Optional[Callable] = None,
            validate_token: Optional[Callable] = None
    ):
        self.ngram_sizes = [1, 2, 3] if ngram_sizes is None else ngram_sizes
        self.exclude_ngram_filter = (lambda x: False) if exclude_ngram_filter is None else exclude_ngram_filter
        self.text_from_token = (lambda tok: tok.lower_) if text_from_token is None else text_from_token
        self.validate_token = (lambda tok: True) if validate_token is None else validate_token

    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(
            self,
            doc
    ) -> List[Tuple[str, List[Union[int, List[Tuple[int, int]]]]]]:
        offset_tokens = {}
        for sent in doc.sents:
            sent_features = []
            for tok in sent:
                if self.validate_token(tok):
                    sent_features.append([
                        tok.idx,
                        tok.idx + len(tok),
                        self.text_from_token(tok)
                    ])
            for ngram_size in self.ngram_sizes:
                if len(sent_features) >= ngram_size:
                    for ngram in window(sent_features, ngram_size):
                        if not self.exclude_ngram_filter(ngram):
                            toktext = ' '.join(x[2] for x in ngram)
                            token_stats = offset_tokens.setdefault(toktext, [0, []])
                            token_stats[0] += 1
                            start, end = ngram[0][0], ngram[-1][1]
                            token_stats[1].append((start, end))
        return list(offset_tokens.items())


# Good for stylistic analysis
PosStopgramFeatures = FlexibleNGramFeatures(
    ngram_sizes=[1, 2, 3],
    text_from_token=(
        lambda tok: (tok.tag_
                     if (tok.lower_ not in MY_ENGLISH_STOP_WORDS
                         or tok.tag_[:2] in ['VB', 'NN', 'JJ', 'RB', 'FW'])
                     else tok.lower_)
    ),
    validate_token=lambda tok: tok.tag_ != '_SP'
)
