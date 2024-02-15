'''
All data from
Johan Bollen, Marijn ten Thij, Fritz Breithaupt, Alexander T. J. Barron, Lauren A. Rutter, Lorenzo Lorenzo-Luaces,
Marten Scheffer. Historical language records reveal a surge of cognitive distortions in recent decades.
Proceedings of the National Academy of Sciences Jul 2021, 118 (30) e2102061118; DOI: 10.1073/pnas.210206111
'''
import pkgutil
import io
import bz2
from typing import List, Tuple

import pandas as pd

from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter


class RogetOffsetGetter(FeatAndOffsetGetter):
    def __init__(self, ):
        self.lex_dict = pd.read_csv(
            io.BytesIO(
                bz2.decompress(
                    pkgutil.get_data('scattertext', 'data/roget.csv.bz2')
                )
            ), names=['term', 'category']
        ).set_index('term')['category'].to_dict()

    def get_term_offsets(self, doc) -> List[Tuple[str, List[Tuple[int, int]]]]:
        return []

    def get_metadata_offsets(self, doc) -> List[Tuple[str, List[Tuple[int, int]]]]:
        offset_tokens = {}
        for tok in doc:
            match = self.lex_dict.get(tok.lower_)
            if match is not None:
                token_stats = offset_tokens.setdefault(match, [0, []])
                token_stats[0] += 1
                token_stats[1].append((tok.idx, tok.idx + len(tok)))
        return list(offset_tokens.items())
