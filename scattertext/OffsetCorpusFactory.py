import string

import numpy as np

from scattertext.OffsetCorpus import OffsetCorpus

from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.indexstore.IndexStore import IndexStore


class OffsetCorpusFactory(object):
    def __init__(self,
                 df,
                 parsed_col,
                 feat_and_offset_getter,
                 category_col=None):

        '''
        Parameters
        ----------
        df : pd.DataFrame
         contains category_col, and parse_col, were parsed col is entirely spacy docs
        parsed_col : str
            name of spacy parsed column in convention_df
        feats_from_spacy_doc : FeatsFromSpacyDoc
        category_col : str, Optional
            name of category column in df; if None, all category names will be '_'
        '''
        self._df = df.reset_index()
        self._category_col = category_col
        self._parsed_col = parsed_col
        self._category_idx_store = IndexStore()
        self._X_factory = CSRMatrixFactory()
        self._mX_factory = CSRMatrixFactory()
        self._term_idx_store = IndexStore()
        self._metadata_idx_store = IndexStore()
        self._feat_and_offset_getter = feat_and_offset_getter
        self._term_offsets = {}
        self._metadata_offsets = {}

    def build(self, show_progress=False):
        '''Constructs the term doc matrix.

        Returns
        -------
        scattertext.ParsedCorpus.ParsedCorpus
        '''
        self._ensure_category_col_is_in_df()

        y = self._get_y_and_populate_category_idx_store(self._df[self._category_col])
        if show_progress is True:
            self._df.progress_apply(self._add_to_x_factory, axis=1)
        else:
            self._df.apply(self._add_to_x_factory, axis=1)

        self._mX = self._mX_factory.set_last_row_idx(len(y) - 1).get_csr_matrix()
        return OffsetCorpus(
            df=self._df,
            X=self._X_factory.set_last_row_idx(len(y) - 1).get_csr_matrix(),
            mX=self._mX_factory.set_last_row_idx(len(y) - 1).get_csr_matrix(),
            y=y,
            term_idx_store=self._term_idx_store,
            category_idx_store=self._category_idx_store,
            metadata_idx_store=self._metadata_idx_store,
            parsed_col=self._parsed_col,
            category_col=self._category_col,
            term_offsets=self._term_offsets,
            metadata_offsets=self._metadata_offsets
        )

    def _ensure_category_col_is_in_df(self):
        if self._category_col not in self._df:
            self._category_col = 'Category'
            while self._category_col in self._df:
                self._category_col = 'Category_' + ''.join(np.random.choice(string.ascii_letters) for _ in range(5))

    def _get_y_and_populate_category_idx_store(self, categories):
        return np.array(categories.apply(self._category_idx_store.getidx))

    def _add_to_x_factory(self, row):
        parsed_text = row[self._parsed_col]
        for term, (count, offsets) in self._feat_and_offset_getter.get_term_offsets(parsed_text):
            term_idx = self._term_idx_store.getidx(term)
            self._X_factory[row.name, term_idx] = count
            if offsets is not None:
                self._term_offsets.setdefault(term, {}).setdefault(row.name, []).extend(offsets)

        for meta, (val, offsets) in self._feat_and_offset_getter.get_metadata_offsets(parsed_text):
            meta_idx = self._metadata_idx_store.getidx(meta)
            self._mX_factory[row.name, meta_idx] = val
            if offsets is not None:
                self._metadata_offsets.setdefault(meta, {}).setdefault(row.name, []).extend(offsets)
