import sys

import pandas as pd

from scattertext.Corpus import Corpus
from scattertext.indexstore.IndexStore import IndexStore


class ParsedCorpus(Corpus):
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
                 unigram_frequency_path=None):
        '''

        Parameters
        ----------
        convention_df pd.DataFrame, contains parsed_col and metadata
        X, csr_matrix
        mX csr_matrix
        y, np.array
        term_idx_store, IndexStore
        category_idx_store, IndexStore
        parsed_col str, column in convention_df containing parsed documents
        category_col str, columns in convention_df containing category
        unigram_frequency_path str, None by default, path of unigram counts file
        '''
        self._df = df
        self._parsed_col = parsed_col
        self._category_col = category_col
        Corpus.__init__(self, X, mX, y, term_idx_store, category_idx_store,
                                           metadata_idx_store,
                                           self._df[self._parsed_col],
                                           unigram_frequency_path)

    def get_texts(self):
        '''
        Returns
        -------
        pd.Series, all raw documents
        '''
        if sys.version_info[0] == 2:
            return self._df[self._parsed_col]
        return self._df[self._parsed_col].apply(str)

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

    def get_parsed_docs(self):
        '''
        Returns
        -------
        pd.Series, Doc represententions of texts.
        '''
        return self._df[self._parsed_col]

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

    def _document_index_mask(self, ngram):
        idx = self._term_idx_store.getidxstrict(ngram.lower())
        mask = (self._X[:, idx] > 0).todense().A1
        return mask

    def term_group_freq_df(self, group_col):
        # type: (str) -> pd.DataFrame
        '''
        Returns a dataframe indexed on the number of groups a term occured in.

        Parameters
        ----------
        group_col

        Returns
        -------
        pd.DataFrame
        '''
        group_idx_store = IndexStore()
        X = self._X
        group_idx_to_cat_idx, row_group_cat \
            = self._get_group_docids_and_index_store(X, group_col, group_idx_store)
        newX = self._change_document_type_in_matrix(X, row_group_cat)
        newX = self._make_all_positive_data_ones(newX)
        category_row = newX.tocoo().row
        for group_idx, cat_idx in group_idx_to_cat_idx.items():
            category_row[category_row == group_idx] = cat_idx
        catX = self._change_document_type_in_matrix(newX, category_row)
        return self._term_freq_df_from_matrix(catX)

    def _make_new_term_doc_matrix(self,
                                  new_X,
                                  new_mX,
                                  new_y,
                                  new_term_idx_store,
                                  new_category_idx_store,
                                  new_metadata_idx_store,
                                  new_y_mask):
        return ParsedCorpus(
            X=new_X if new_X is not None else self._X,
            mX=new_mX if new_mX is not None else self._mX,
            y=new_y if new_y is not None else self._y,
            parsed_col=self._parsed_col,
            category_col=self._category_col,
            term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
            category_idx_store=new_category_idx_store if new_category_idx_store is not None else self._category_idx_store,
            metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
            df=self._df[new_y_mask] if new_y_mask is not None else self._df,
            unigram_frequency_path=self._unigram_frequency_path
        )

    def _get_group_docids_and_index_store(self, X, group_col, group_idx_store):
        row_group_cat = X.tocoo().row
        group_idx_to_cat_idx = {}
        for doc_idx, row in self._df.iterrows():
            group_idx = group_idx_store.getidx(row[group_col] + '-' + row[self._category_col])
            row_group_cat[row_group_cat == doc_idx] = group_idx
            group_idx_to_cat_idx[group_idx] = self._y[doc_idx]
        return group_idx_to_cat_idx, row_group_cat
