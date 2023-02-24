import pandas as pd
from tqdm.auto import tqdm

class TokenSequenceSegmenter:
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
            for i in range(max(len(doc) // self.segment_length, 1)):
                start_token_idx = self.segment_length * (i)
                end_token_idx = -1 if self.segment_length * (i + 1) >= len(doc) else self.segment_length * (i + 1)
                start_idx = doc[start_token_idx].idx
                end_idx = doc[end_token_idx].idx + len(doc[end_token_idx])
                segment_text = str(doc)[start_idx:end_idx]
                segment_data.append({
                    'Text': segment_text,
                    'DocIdx': doc_i,
                    'SegmentIdx': i
                })
        return pd.DataFrame(segment_data)

