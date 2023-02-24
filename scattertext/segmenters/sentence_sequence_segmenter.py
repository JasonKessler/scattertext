import pandas as pd
from tqdm.auto import tqdm


class SentenceSequenceSegmenter:
    def __init__(
            self,
            segment_length: int = 500
    ):
        self.segment_length = segment_length

    def whole_df_to_segmented_df(
            self,
            df: pd.DataFrame,
            parsed_col: str,
            verbose: bool = False
    ) -> pd.DataFrame:
        assert parsed_col in df.columns
        segment_data = []
        docit = enumerate(df[parsed_col])
        if verbose:
            docit = tqdm(docit, total=len(df))
        for doc_i, doc in docit:
            segment = []
            segment_len = 0
            segment_idx = 0
            for _, sent in enumerate(doc.sents):
                if segment_len == 0:
                    segment = [sent]
                    segment_len += len(sent)
                elif segment_len + len(sent) > self.segment_length:
                    segment_data.append({
                        'Text': str(doc[segment[0][0].i:segment[-1][-1].i + 1]),
                        'DocIdx': doc_i,
                        'SegmentIdx': segment_idx
                    })
                    segment_idx += 1
                    segment = []
                    segment_len = 0
                else:
                    segment.append(sent)
                    segment_len += len(sent)
            if segment_len > 0:
                segment_data.append({
                    'Text': str(doc[segment[0][0].i:segment[-1][-1].i + 1]),
                    'DocIdx': doc_i,
                    'SegmentIdx': segment_idx
                })
        return pd.DataFrame(segment_data)
