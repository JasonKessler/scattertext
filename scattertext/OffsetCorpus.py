from scattertext.DataFrameCorpus import DataFrameCorpus
from scattertext.ParsedCorpus import ParsedDataFrameCorpus


class OffsetCorpus(ParsedDataFrameCorpus):
    def __init__(self,
                 df,
                 X,
                 mX,
                 y,
                 term_idx_store,
                 category_idx_store,
                 metadata_idx_store,
                 parsed_col,
                 category_col,
                 term_offsets,
                 metadata_offsets,
                 unigram_frequency_path=None):
        self._term_offsets = term_offsets
        self._metadata_offsets = metadata_offsets
        ParsedDataFrameCorpus.__init__(self, parsed_col, category_col)
        DataFrameCorpus.__init__(self, X, mX, y, term_idx_store, category_idx_store,
                                 metadata_idx_store,
                                 df[self._parsed_col],
                                 df,
                                 unigram_frequency_path)

    def get_offsets(self):
        return self._metadata_offsets

    def _make_new_term_doc_matrix(self,
                                  new_X=None,
                                  new_mX=None,
                                  new_y=None,
                                  new_term_idx_store=None,
                                  new_category_idx_store=None,
                                  new_metadata_idx_store=None,
                                  new_y_mask=None,
                                  new_df=None,
                                  new_term_offsets=None,
                                  new_metadata_offsets=None):

        X, mX, y = self._update_X_mX_y(new_X, new_mX, new_y, new_y_mask)
        metadata_offsets, term_offsets = self._update_offsets(new_metadata_idx_store, new_metadata_offsets,
                                                              new_term_idx_store, new_term_offsets)

        return OffsetCorpus(
            X=X,
            mX=mX,
            y=y,
            parsed_col=self._parsed_col,
            category_col=self._category_col,
            term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
            category_idx_store=new_category_idx_store if new_category_idx_store is not None \
                else self._category_idx_store,
            metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None \
                else self._metadata_idx_store,
            df=self._apply_mask_to_df(new_y_mask, new_df),
            term_offsets=term_offsets,
            metadata_offsets=metadata_offsets,
            unigram_frequency_path=self._unigram_frequency_path,
        )

    def _update_offsets(self, new_metadata_idx_store, new_metadata_offsets, new_term_idx_store, new_term_offsets):
        term_offsets = self._term_offsets if new_term_offsets is None else new_term_offsets
        metadata_offsets = self._metadata_offsets if new_metadata_offsets is None else new_metadata_offsets
        if new_term_idx_store is not None:
            term_offsets = {k: term_offsets[k] for k in new_term_idx_store.values()}
        if new_metadata_idx_store is not None:
            metadata_offsets = {k: metadata_offsets[k] for k in new_metadata_idx_store.values()}
        return metadata_offsets, term_offsets
