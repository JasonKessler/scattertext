import re
from typing import Dict, List, Optional, Callable, Tuple

from spacy.tokens import Doc

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter

class RegexFeatAndOffsetGetter(FeatAndOffsetGetter):
    def __init__(self,
                 regex_dict: Dict[str, str],
                 flags: int = re.U | re.I | re.M,
                 span_getter: Optional[Callable[[re.Match], Tuple[int, int]]] = None):
        '''

        :param regex_dict: dict
            This should be a dictionary mapping a label to the text of a regular expression
            e.g., {'AorB': r'(a|b)', 'Number: r'\d+'}
        :param flags: int, default re.U | re.I | re.M
            Same as re   flags
        :param span_getter : Optional[Callable[[re.Match], Tuple[int, int]]]
            Takes a match and returns a span. default: `lambda match: match.span()`
        '''
        self.flags = flags
        self.labeled_regexes = [[k, re.compile(v, self.flags)] for k, v in regex_dict.items()]
        if span_getter is None:
            self.span_getter = lambda match: match.span()
        else:
            self.span_getter = span_getter

    def get_term_offsets(self, doc: Doc) -> List[Tuple[str, List[Tuple[int, int]]]]:
        return []

    def get_metadata_offsets(self, doc: Doc) -> List[Tuple[str, List[Tuple[int, int]]]]:
        text = str(doc)
        offset_tokens = {}
        for label, regex in self.labeled_regexes:
            for match in regex.finditer(text):
                token_stats = offset_tokens.setdefault(label, [0, []])
                token_stats[0] += 1
                span = self.span_getter(match)
                token_stats[1].append(span)
        return list(offset_tokens.items())