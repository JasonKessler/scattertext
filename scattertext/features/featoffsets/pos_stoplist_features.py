
from typing import List, Tuple, Union, Optional
from collections import deque

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter
from scattertext.Common import ENGLISH_STOP_WORDS


def window(seq, n=2):
    it = iter(seq)
    win = deque((next(it, None) for _ in range(n)), maxlen=n)
    yield list(win)
    append = win.append
    for e in it:
        append(e)
        yield list(win)


class PosStopgramFeatures(FeatAndOffsetGetter):
    def __init__(
            self,
            ngram_sizes: Optional[List[int]] = None
    ):
        self.ngram_sizes = [1, 2, 3] if ngram_sizes is None else ngram_sizes

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
                tok_text = tok.lower_
                if tok.lower_ not in ENGLISH_STOP_WORDS or (tok.tag_[:2] in ['VB', 'NN', 'JJ']):
                    tok_text = tok.tag_
                sent_features.append([tok.idx, tok.idx + len(tok), tok_text])
            for ngram_size in self.ngram_sizes:
                if len(sent_features) >= ngram_size:
                    for ngram in window(sent_features, ngram_size):
                        toktext = ' '.join(x[2] for x in ngram)
                        token_stats = offset_tokens.setdefault(toktext, [0, []])
                        token_stats[0] += 1
                        start, end = ngram[0][0], ngram[-1][1]
                        token_stats[1].append((start, end))
        return list(offset_tokens.items())
