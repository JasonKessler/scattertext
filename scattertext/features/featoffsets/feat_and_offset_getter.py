from typing import List, Tuple


class FeatAndOffsetGetter(object):
    def get_term_offsets(self, doc) -> List[Tuple[str, List[Tuple[int, int]]]]:
        return []

    def get_metadata_offsets(self, doc) -> List[Tuple[str, List[Tuple[int, int]]]]:
        return []

    def get_metadata_row_offsets(self, doc, row):
        return []