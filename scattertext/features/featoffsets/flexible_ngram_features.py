from typing import List, Tuple, Union, Optional, Callable, Dict
from collections import deque

import spacy.tokens

from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter
from scattertext.Common import MY_ENGLISH_STOP_WORDS


def sequence_window(seq, n=2):
    # adapted from https://stackoverflow.com/questions/46516730/how-to-work-with-zip-on-2-generators-s-t-each-returns-the-same-item-that-changes
    it = iter(seq)
    win = deque((next(it, None) for _ in range(n)), maxlen=n)
    yield list(win)
    for e in it:
        win.append(e)
        yield list(win)


class FlexibleNGramFeaturesBase:
    def __init__(self,
                 exclude_ngram_filter: Optional[Callable[[str], bool]] = None,
                 ngram_sizes: Optional[List[int]] = None,
                 text_from_token: Optional[Callable[[str], str]] = None,
                 validate_token: Optional[Callable[[spacy.tokens.Token], bool]] = None,
                 whitespace_substitute: Optional[Callable[[str], str]] = None):
        self.exclude_ngram_filter = (lambda x: False) if exclude_ngram_filter is None else exclude_ngram_filter
        self.ngram_sizes = [1, 2, 3] if ngram_sizes is None else ngram_sizes
        self.text_from_token = (lambda tok: tok.lower_) if text_from_token is None else text_from_token
        self.validate_token = (lambda tok: tok.tag_ != '_SP' and tok.orth_.strip() != '') \
            if validate_token is None else validate_token
        self.whitespace_substitute = ' ' if whitespace_substitute is None else whitespace_substitute

    def _doc_to_feature_representation(self, doc) -> Dict:
        offset_tokens = {}
        for sent in doc.sents:
            sent_features = sent  # self._sent_to_token_features(sent)
            for ngram_size in self.ngram_sizes:
                if len(sent_features) >= ngram_size:
                    for ngram in sequence_window(sent_features, ngram_size):
                        if not self.exclude_ngram_filter(ngram):
                            self._add_ngram_to_token_stats(ngram, offset_tokens)
        return offset_tokens

    def _add_ngram_to_token_stats(self, ngram, offset_tokens):
        toktext = self.whitespace_substitute.join(self.text_from_token(tok) for tok in ngram)
        token_stats = offset_tokens.setdefault(toktext, [0, []])
        token_stats[0] += 1
        start = ngram[0].idx
        end = ngram[-1].idx + len(ngram[-1].orth_)
        token_stats[1].append((start, end))

    def _sent_to_token_features(self, sent):
        sent_features = []
        for tok in sent:
            if self.validate_token(tok):
                sent_features.append([
                    tok.idx,
                    tok.idx + len(tok),
                    self.text_from_token(tok)
                ])
        return sent_features


class FlexibleNGramFeatures(FeatAndOffsetGetter, FlexibleNGramFeaturesBase):
    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(
            self,
            doc
    ) -> List[Tuple[str, List[Tuple[int, List[Tuple[int, int]]]]]]:
        offset_tokens = self._doc_to_feature_representation(doc)
        return list(offset_tokens.items())


class FlexibleNGrams(FeatsFromSpacyDoc, FlexibleNGramFeaturesBase):
    def __init__(
            self,
            ngram_sizes: Optional[List[int]] = None,
            exclude_ngram_filter: Optional[Callable] = None,
            text_from_token: Optional[Callable] = None,
            validate_token: Optional[Callable] = None
    ):
        FeatsFromSpacyDoc.__init__(self)
        FlexibleNGramFeaturesBase.__init__(self, exclude_ngram_filter, ngram_sizes, text_from_token, validate_token)

    def get_feats(self, doc):
        return self._doc_to_feature_representation(doc)

    def _add_ngram_to_token_stats(self, ngram, offset_tokens):
        # toktext = ' '.join(x[2] for x in ngram)
        toktext = ' '.join(self.text_from_token(tok) for tok in ngram)
        offset_tokens.setdefault(toktext, 0)
        offset_tokens[toktext] += 1


# Good for stylistic analysis
PosStopgramFeatures = FlexibleNGramFeatures(
    ngram_sizes=[1, 2, 3],
    text_from_token=(
        lambda tok: (tok.tag_
                     if (tok.lower_ not in MY_ENGLISH_STOP_WORDS
                         or tok.tag_[:2] in ['VB', 'NN', 'JJ', 'RB', 'FW'])
                     else tok.lower_)
    )
)
