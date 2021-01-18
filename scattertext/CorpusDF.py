import pandas as pd

from scattertext.DataFrameCorpus import DataFrameCorpus


class CorpusDF(DataFrameCorpus):
    def __init__(self,
                 df,
                 X,
                 mX,
                 y,
                 text_col,
                 term_idx_store,
                 category_idx_store,
                 metadata_idx_store,
                 unigram_frequency_path=None):
        '''
        Parameters
        ----------
        X : csr_matrix
            term document matrix
        mX : csr_matrix
            metadata-document matrix
        y : np.array
            category index array
        term_idx_store : IndexStore
            Term indices
        category_idx_store : IndexStore
            Catgory indices
        metadata_idx_store : IndexStore
          Document metadata indices
        text_col: np.array or pd.Series
            Raw texts
        unigram_frequency_path : str or None
            Path to term frequency file.
        '''
        self._text_col = text_col
        DataFrameCorpus.__init__(self,
                                 X,
                                 mX,
                                 y,
                                 term_idx_store,
                                 category_idx_store,
                                 metadata_idx_store,
                                 df[text_col],
                                 df,
                                 unigram_frequency_path)

    def get_texts(self):
        '''
        Returns
        -------
        pd.Series, all raw documents
        '''
        return self._df[self._text_col]


    def _make_new_term_doc_matrix(self,
                                  new_X=None,
                                  new_mX=None,
                                  new_y=None,
                                  new_term_idx_store=None,
                                  new_category_idx_store=None,
                                  new_metadata_idx_store=None,
                                  new_y_mask=None,
                                  new_df=None):
        X, mX, y = self._update_X_mX_y(new_X, new_mX, new_y, new_y_mask)

        return CorpusDF(
            df=self._apply_mask_to_df(new_y_mask, new_df),
            X=X,
            mX=mX,
            y=y,
            term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
            category_idx_store=new_category_idx_store if new_category_idx_store is not None else self._category_idx_store,
            metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
            text_col=self._text_col,
            unigram_frequency_path=self._unigram_frequency_path
        )
