from scattertext.indexstore import IndexStore

from scattertext.Corpus import Corpus


class DataFrameCorpus(Corpus):
    def __init__(self,
                 X,
                 mX,
                 y,
                 term_idx_store,
                 category_idx_store,
                 metadata_idx_store,
                 raw_texts,
                 df,
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
        raw_texts : np.array or pd.Series
            Raw texts
        unigram_frequency_path : str or None
            Path to term frequency file.
        '''
        self._df = df
        Corpus.__init__(self, X, mX, y,
                        term_idx_store,
                        category_idx_store,
                        metadata_idx_store,
                        raw_texts,
                        unigram_frequency_path)

    def _apply_mask_to_df(self, new_y_mask, new_df):
        df_to_ret = self._df if new_df is None else new_df
        if new_y_mask is None:
            return df_to_ret

        return df_to_ret[new_y_mask].reset_index(drop=True)

    def get_df(self):
        '''
        Returns
        -------
        pd.DataFrame
        '''
        return self._df

    def get_field(self, field):
        '''
        Parameters
        ----------
        field: str, field name

        Returns
        -------
        pd.Series, all members of field
        '''
        return self._df[field]

    def assign(self, **kwargs):
        '''
        Runs assign in the internal dataframe

        :param kwargs:
        :return: Corpus
        '''
        self._df = self._df.assign(**kwargs)
        return self

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

    def make_column_metadata(self, column):
        '''

        :param column: str
        :return: Corpus
        '''

        return self.add_doc_names_as_metadata(self.get_df()[column])
