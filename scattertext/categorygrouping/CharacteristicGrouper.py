import abc
from typing import List, Optional, Callable, Tuple, Any, Dict

import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

from scattertext import TermDocMatrix, RankDifference


class CategoryEmbedderABC:
    @abc.abstractmethod
    def embed_categories(self, corpus: TermDocMatrix) -> np.array:
        pass


class RankEmbedder(CategoryEmbedderABC):
    def __init__(self,
                 scorer: Optional[Callable[[np.array, np.array], np.array]] = None,
                 rank_threshold: int = 10,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scorer = RankDifference().get_scores if scorer is None else scorer
        self.rank_threshold = rank_threshold

    def embed_categories(self, corpus: TermDocMatrix) -> np.array:
        tdf = corpus.get_term_freq_df('')
        term_freqs = tdf.sum(axis=1)

        score_df = pd.DataFrame({
            category: pd.Series(
                self.scorer(tdf[category], term_freqs - tdf[category]),
                index=corpus.get_terms()
            ).sort_values(ascending=False).head(self.rank_threshold)
            for category in corpus.get_categories()
        })

        return score_df.fillna(0).T.values


class CharacteristicGrouper:
    def __init__(
            self,
            corpus: TermDocMatrix,
            window_size: int = 1,
            rank_embedder: Optional[CategoryEmbedderABC] = None,
            distance_measure: Callable[[np.array, np.array], float] = None
    ):
        self.corpus = corpus
        self.window_size = window_size
        self.rank_embedder = RankEmbedder() if rank_embedder is None else RankEmbedder
        self.distance_measure = cosine if distance_measure is None else distance_measure

    def group_corpus_categories(
            self,
            category_order: Optional[List[str]] = None,
            number_of_splits: int = 10
    ) -> TermDocMatrix:
        category_to_bin_dict = self.get_category_group_dict(category_order, number_of_splits)
        return self.corpus.recategorize(
            [category_to_bin_dict[self.corpus.get_categories()[c]]
             for c in self.corpus.get_category_ids()]
        )

    def get_category_group_dict(
            self,
            category_order: List[str] = None,
            number_of_splits: int = 10
    ) -> Dict[str, str]:
        category_order = sorted(self.corpus.get_categories()) if category_order is None else category_order
        assert len(category_order) == self.corpus.get_num_categories()
        embedding_mat = self.rank_embedder.embed_categories(corpus=self.corpus)
        cat_boundaries = self.__get_change_point_candidates(
            embeddings=embedding_mat,
            ordered_category_names=category_order,
        ).iloc[:number_of_splits].sort_values(by='Order')
        intervals = []
        interval_names = []
        last = 0
        for _, row in cat_boundaries.iterrows():
            intervals.append((last, int(row.Order)))
            interval_names.append(
                category_order[last + 1 if last > 0 else 0] + '-' + category_order[int(row.Order)])
            last = int(row.Order)
        intervals.append((last, len(category_order)))
        interval_names.append(category_order[last + 1] + '-' + category_order[-1])
        interval_index = pd.IntervalIndex.from_tuples(intervals)
        category_to_bin_dict = {category: interval_names[interval_index.get_loc(i) if i > 0 else 0]
                                for i, category in enumerate(category_order)}
        return category_to_bin_dict

    def __get_change_point_candidates(
            self,
            embeddings: np.array,
            ordered_category_names: List[str],
    ) -> pd.DataFrame:

        category_index_df = pd.DataFrame({
            'Category': self.corpus.get_categories(),
        }).reset_index().set_index('Category').loc[
            ordered_category_names
        ].assign(
            Order=lambda df: np.arange(len(df))
        )

        mat = embeddings[:, category_index_df['index'].values]

        dists = []
        for i in range(mat.shape[1] - self.window_size):
            a = mat[:, list(range(max(0, i - self.window_size + 1), i + 1))].mean(axis=1)
            b = mat[:, list(range(i + 1, max(i + 1 + self.window_size, mat.shape[1])))].mean(axis=1)
            distance = np.linalg.norm(a * b) / (np.linalg.norm(a) * np.linalg.norm(b))
            dists.append(distance)

        return category_index_df.assign(
            Dist=dists + [0] * self.window_size,
        ).sort_values(by='Dist', ascending=False)
