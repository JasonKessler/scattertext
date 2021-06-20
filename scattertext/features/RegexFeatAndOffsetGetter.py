import re

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter


class RegexFeatAndOffsetGetter(FeatAndOffsetGetter):
    def __init__(self, regex_dict):
        '''

        :param regex_dict: dict
            This should be a dictionary mapping a label to the text of a regular expression
            e.g., {'AorB': r'(a|b)', 'Number: r'\d+'}
        '''
        self.labeled_regexes = [[k, re.compile(v)] for k, v in regex_dict.items()]

    def get_term_offsets(self, doc):
        return []

    def get_metadata_offsets(self, doc):
        text = str(doc)
        offset_tokens = {}
        for label, regex in self.labeled_regexes:
            for match in regex.finditer(text, re.I | re.M):
                token_stats = offset_tokens.setdefault(label, [0, []])
                token_stats[0] += 1
                token_stats[1].append(match.span())
        return list(offset_tokens.items())