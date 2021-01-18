from typing import Optional, List
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix

from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.CorpusDF import CorpusDF
from scattertext.indexstore import IndexStore, IndexStoreFromList


class CorpusFromTermFrequencies(object):
    def __init__(self,
                 X: csr_matrix,
                 term_vocabulary: List[str],
                 mX: Optional[csr_matrix] = None,
                 y: Optional[np.array] = None,
                 category_names: Optional[str] = None,
                 metadata_vocabulary: Optional[List[str]] = None,
                 text_df: Optional[pd.DataFrame] = None,
                 text_col: Optional[str] = None,
                 parsed_col: Optional[str] = None,
                 category_col: Optional[str] = None,
                 unigram_frequency_path: Optional[str] = None):
        '''
        Parameters
        ----------
        X: csr_matrix; term-document frequency matrix; columns represent terms and rows documents
        term_vocabulary: List[str]; Each entry corresponds to a term
        mX: Optional[csr_matrix]; metadata csr matrix
        y: Optional[np.array[int]]; indices of category names for each document
        category_names: Optional[List[str]], names of categories for y
        text_df: pd.DataFrame with a row containing the raw document text
        text_col: str; name of row containing the text of each document
        parsed_col: str; name of row containing the parsed text of each document
        unigram_frequency_path: str (see TermDocMatrix)

        '''
        self.X = X
        self.term_idx_store = IndexStoreFromList.build(term_vocabulary)
        assert self.X.shape[1] == len(term_vocabulary)
        self.metadata_idx_store = IndexStore()
        if y is None:
            self.y = np.zeros(self.X.shape[0], dtype=np.int)
            self.category_idx_store = IndexStoreFromList.build(['_'])
            assert category_names is None
        else:
            self.y = y
            assert len(category_names) == len(set(y))
            self.category_idx_store = IndexStoreFromList.build(category_names)
        if metadata_vocabulary is not None:
            assert mX.shape[1] == metadata_vocabulary
            self.mX = mX
            self.metadata_idx_store = IndexStoreFromList.build(metadata_vocabulary)
        else:
            assert metadata_vocabulary is None
            self.mX = csr_matrix((0, 0))
            self.metadata_idx_store = IndexStore()
        self.text_df = text_df
        if parsed_col is not None:
            assert parsed_col in text_df
        if text_col is not None:
            assert text_col in text_df
        if category_col is not None:
            assert category_col in text_df
        self.category_col = category_col
        self.text_col = text_col
        self.parsed_col = parsed_col
        self.unigram_frequency_path = unigram_frequency_path

    def build(self):
        '''
        Returns
        -------
        CorpusDF
        '''
        if self.text_df is not None:
            if self.parsed_col is not None:
                if self.category_col is None:
                    self.text_df = self.text_df.assign(Category=self.category_idx_store.getvalbatch(self.y))
                    self.category_col = 'Category'
                return ParsedCorpus(
                    df=self.text_df,
                    X=self.X,
                    mX=self.mX,
                    y=self.y,
                    parsed_col=self.parsed_col,
                    term_idx_store=self.term_idx_store,
                    category_idx_store=self.category_idx_store,
                    metadata_idx_store=self.metadata_idx_store,
                    unigram_frequency_path=self.unigram_frequency_path,
                    category_col=self.category_col
                )
            elif self.text_col is not None:
                return CorpusDF(
                    df=self.text_df,
                    X=self.X,
                    mX=self.mX,
                    y=self.y,
                    text_col=self.text_col,
                    term_idx_store=self.term_idx_store,
                    category_idx_store=self.category_idx_store,
                    metadata_idx_store=self.metadata_idx_store,
                    unigram_frequency_path=self.unigram_frequency_path
                )
        return TermDocMatrix(
            X=self.X,
            mX=self.mX,
            y=self.y,
            term_idx_store=self.term_idx_store,
            category_idx_store=self.category_idx_store,
            metadata_idx_store=self.metadata_idx_store,
            unigram_frequency_path=self.unigram_frequency_path
        )
