from copy import copy
from typing import List, Tuple, Self, Dict

from scattertext.TermDocMatrixWithoutCategories import MetadataReplacementRetentionPolicy
from scattertext.ParsedCorpus import ParsedCorpus


class OffsetCorpus(ParsedCorpus):
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
        ParsedCorpus.__init__(self,
                              df=df,
                              X=X,
                              mX=mX,
                              y=y,
                              term_idx_store=term_idx_store,
                              category_idx_store=category_idx_store,
                              metadata_idx_store=metadata_idx_store,
                              parsed_col=parsed_col,
                              category_col=category_col,
                              unigram_frequency_path=unigram_frequency_path)

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
        metadata_offsets, term_offsets = self._update_offsets(
            new_metadata_idx_store=new_metadata_idx_store,
            new_metadata_offsets=new_metadata_offsets,
            new_term_idx_store=new_term_idx_store,
            new_term_offsets=new_term_offsets
        )

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

    def _update_offsets(
            self,
            new_metadata_idx_store,
            new_metadata_offsets,
            new_term_idx_store,
            new_term_offsets
    ):
        term_offsets = self._term_offsets if new_term_offsets is None else new_term_offsets
        metadata_offsets = self._metadata_offsets if new_metadata_offsets is None else new_metadata_offsets
        if new_term_idx_store is not None:
            term_offsets = {k: term_offsets[k] for k in new_term_idx_store.values()}

        if new_metadata_idx_store is not None:
            metadata_offsets = {k: metadata_offsets[k] for k in new_metadata_idx_store.values()}
        return metadata_offsets, term_offsets

    def rename_metadata(
            self,
            old_to_new_vals: List[Tuple[str, str]],
            policy: MetadataReplacementRetentionPolicy = MetadataReplacementRetentionPolicy.KEEP_ONLY_NEW
    ) -> Self:
        new_mX, new_metadata_idx_store = self._remap_metadata(old_to_new_vals, policy=policy)
        new_metadata_offsets = self._remap_offsets(old_to_new_vals, policy)

        return self._make_new_term_doc_matrix(
            new_X=self._X,
            new_mX=new_mX,
            new_y=self._y,
            new_term_idx_store=self._term_idx_store,
            new_category_idx_store=self._category_idx_store,
            new_metadata_idx_store=new_metadata_idx_store,
            new_y_mask=self._y == self._y,
            new_metadata_offsets=new_metadata_offsets
        )

    def _remap_offsets(
            self,
            old_to_new_vals: List[Tuple[str, str]],
            policy: MetadataReplacementRetentionPolicy = MetadataReplacementRetentionPolicy.KEEP_ONLY_NEW
    ) -> Dict[str, Dict[int, List[Tuple[int, int]]]]:
        old_to_new_df = self._get_old_to_new_metadata_mapping_df(old_to_new_vals)
        keep_vals = self._get_metadata_mapped_values_to_keep(old_to_new_df)
        new_metadata_offsets = {}
        for new_val, new_df in old_to_new_df.groupby('New'):
            new_count_offsets = {}
            for old in new_df.Old.values:
                old_offsets = self._metadata_offsets.get(old, [])
                for doc_id, offsets in old_offsets.items():
                    new_count_offsets.setdefault(doc_id, []).extend(offsets)
            new_metadata_offsets[new_val] = new_count_offsets
            if policy.value == MetadataReplacementRetentionPolicy.KEEP_UNMODIFIED.value:
                for keep_val in keep_vals:
                    new_metadata_offsets[keep_val] = self._metadata_offsets[keep_val]
            elif policy.value == MetadataReplacementRetentionPolicy.KEEP_ALL.value:
                for val in self.get_metadata():
                    new_metadata_offsets[val] = self._metadata_offsets[val]
        return new_metadata_offsets

    def use_categories_as_metadata_and_replace_terms(self):
        '''
        Returns a TermDocMatrix which is identical to self except the metadata values are now identical to the
         categories present and term-doc-matrix is now the metadata matrix.

        :return: TermDocMatrix
        '''
        new_tdm = self._make_new_term_doc_matrix(
            new_X=self._mX,
            new_mX=self._categories_to_metadata_factory(),
            new_y=self._y,
            new_term_idx_store=self._metadata_idx_store,
            new_category_idx_store=self._category_idx_store,
            new_metadata_idx_store=copy(self._category_idx_store),
            new_y_mask=self._y == self._y,
            new_term_offsets=self._metadata_offsets,
            new_metadata_offsets={k: [] for k in self.get_categories()},
        )
        return new_tdm
