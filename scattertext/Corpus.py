import numpy as np
import pandas as pd
from numpy import nonzero

from scattertext.TermDocMatrix import TermDocMatrix


class Corpus(TermDocMatrix):
    def __init__(self,
                 X,
                 mX,
                 y,
                 term_idx_store,
                 category_idx_store,
                 metadata_idx_store,
                 raw_texts,
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
        TermDocMatrix.__init__(self, X, mX, y,
                               term_idx_store,
                               category_idx_store,
                               metadata_idx_store,
                               unigram_frequency_path)
        self._raw_texts = raw_texts

    def get_texts(self):
        '''
        Returns
        -------
        pd.Series, all raw documents
        '''
        return self._raw_texts

    def get_doc_indices(self):
        return self._y.astype(int)

    def search(self, ngram, non_text: bool=False):
        '''
        Parameters
        ----------
        ngram str or unicode, string to search for

        Returns
        -------
        pd.DataFrame, {'texts': <matching texts>, 'categories': <corresponding categories>}

        '''
        mask = self._document_index_mask(ngram, non_text=non_text)
        return pd.DataFrame({
            'text': self.get_texts()[mask],
            'category': [self._category_idx_store.getval(idx)
                         for idx in self._y[mask]]
        })

    def search_index(self, term: str, non_text: bool = False):
        """
        Parameters
        ----------
        ngram str or unicode, string to search for

        Returns
        -------
        np.array, list of matching document indices
        """
        return nonzero(self._document_index_mask(term, non_text))[0]

    def _document_index_mask(self, feature: str, non_text: bool):
        term_idx_store = self.get_term_index_store(non_text=non_text)
        idx = term_idx_store.getidxstrict(feature.lower())
        mask = (self.get_term_doc_mat(non_text=non_text)[:, idx] > 0).todense().A1
        return mask

    def _make_new_term_doc_matrix(self,
                                  new_X=None,
                                  new_mX=None,
                                  new_y=None,
                                  new_term_idx_store=None,
                                  new_category_idx_store=None,
                                  new_metadata_idx_store=None,
                                  new_y_mask=None):
        X, mX, y = self._update_X_mX_y(new_X, new_mX, new_y, new_y_mask)
        return Corpus(X=X,
                      mX=mX,
                      y=y,
                      term_idx_store=new_term_idx_store if new_term_idx_store is not None else self._term_idx_store,
                      category_idx_store=new_category_idx_store if new_category_idx_store is not None else self._category_idx_store,
                      metadata_idx_store=new_metadata_idx_store if new_metadata_idx_store is not None else self._metadata_idx_store,
                      raw_texts=np.array(self.get_texts())[new_y_mask] if new_y_mask is not None else self.get_texts(),
                      unigram_frequency_path=self._unigram_frequency_path)
