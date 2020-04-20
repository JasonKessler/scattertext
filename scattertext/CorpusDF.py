import pandas as pd

from scattertext.Corpus import Corpus


class CorpusDF(Corpus):
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
        self._df = df
        self._text_col = text_col
        Corpus.__init__(self,
                        X,
                        mX,
                        y,
                        term_idx_store,
                        category_idx_store,
                        metadata_idx_store,
                        df[text_col],
                        unigram_frequency_path)

    def get_texts(self):
        '''
        Returns
        -------
        pd.Series, all raw documents
        '''
        return self._df[self._text_col]

    def get_df(self):
        return self._df

    def search(self, ngram):
        '''
        Parameters
        ----------
        ngram, str or unicode, string to search for

        Returns
        -------
        pd.DataFrame, {self._parsed_col: <matching texts>, self._category_col: <corresponding categories>, ...}

        '''
        mask = self._document_index_mask(ngram)
        return self._df[mask]

    def _make_new_term_doc_matrix(self,
                                  new_X=None,
                                  new_mX=None,
                                  new_y=None,
                                  new_term_idx_store=None,
                                  new_category_idx_store=None,
                                  new_metadata_idx_store=None,
                                  new_y_mask=None):
        return CorpusDF(
            df=self._df[new_y_mask] if new_y_mask is not None else self._df,
            X=new_X if new_X is not None else self._X,
            mX=new_mX if new_mX is not None else self._mX,
            y=new_y if new_y is not None else self._y,
            term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
            category_idx_store=new_category_idx_store if new_category_idx_store is not None else self._category_idx_store,
            metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
            text_col=self._text_col,
            unigram_frequency_path=self._unigram_frequency_path
        )
