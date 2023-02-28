from typing import List, Optional, Callable, Dict, Tuple

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from tqdm.auto import tqdm

from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.categorygrouping.characteristic_embedder_base import CategoryEmbedderABC
from scattertext.categorygrouping.rank_embedder import RankEmbedder


def cosine(a: np.array, b: np.array) -> np.array:
    return np.linalg.norm(a * b) / (np.linalg.norm(a) * np.linalg.norm(b))

def spearman_distance(a: np.array, b: np.array) -> np.array:
    return spearmanr(a, b)[0]


class CharacteristicGrouper:
    def __init__(
            self,
            corpus: TermDocMatrix,
            non_text: bool = False,
            window_size: int = 1,
            to_text: str = ' to<br/>',
            rank_embedder: Optional[CategoryEmbedderABC] = None,
            distance_measure: Callable[[np.array, np.array], float] = None
    ):
        self.corpus = corpus
        self.window_size = window_size
        self.rank_embedder = RankEmbedder() if rank_embedder is None else rank_embedder
        self.distance_measure = spearman_distance if distance_measure is None else distance_measure
        self.non_text = non_text
        self.to_text = to_text

    def group_corpus_categories(
            self,
            category_order: Optional[List[str]] = None,
            number_of_splits: int = 10
    ) -> TermDocMatrix:
        new_categories, new_categories_order = self.get_new_doc_categories(category_order, number_of_splits)
        return self.corpus.recategorize(new_categories)

    def get_new_doc_categories(
            self,
            category_order: Optional[List[str]] = None,
            number_of_splits: int = 10,
            verbose=False
    ) -> Tuple[List, List]:
        category_to_bin_dict = self.get_category_group_dict(category_order, number_of_splits, verbose)
        new_categories = [category_to_bin_dict[cat] for cat in self.corpus.get_category_names_by_row()]

        seen = set()
        new_categories_order = [category_to_bin_dict[x] for x in category_order
                                if not (category_to_bin_dict[x] in seen or seen.add(category_to_bin_dict[x]))]
        return new_categories, new_categories_order

    def get_category_group_dict(
            self,
            category_order: List[str] = None,
            number_of_splits: int = 10,
            verbose=False
    ) -> Dict[str, str]:
        category_order = sorted(self._get_categories()) if category_order is None else category_order
        assert len(category_order) == self.corpus.get_num_categories()
        embedding_mat = self.rank_embedder.embed_categories(
            corpus=self.corpus,
            non_text=self.non_text
        )
        cat_boundaries = self.get_change_point_candidates(
            embeddings=embedding_mat,
            ordered_category_names=category_order,
        ).iloc[:number_of_splits].sort_values(by='Order')
        intervals = []
        interval_names = []
        last = 0
        for _, row in cat_boundaries.iterrows():
            intervals.append((last, int(row.Order)))
            interval_names.append(
                str(category_order[last + 1 if last > 0 else 0])
                + self.to_text + str(category_order[int(row.Order)]))
            last = int(row.Order)
        intervals.append((last, len(category_order)))
        interval_names.append(str(category_order[last + 1])
                              + self.to_text + str(category_order[-1]))
        interval_index = pd.IntervalIndex.from_tuples(intervals)
        category_to_bin_dict = {category: interval_names[interval_index.get_loc(i) if i > 0 else 0]
                                for i, category in enumerate(category_order)}
        return category_to_bin_dict

    def _get_string_categories(self) -> List[str]:
        return [str(c) for c in self.corpus.get_categories()]
    def _get_categories(self) -> List[str]:
        return self.corpus.get_categories()

    def get_change_point_candidates(
            self,
            embeddings: np.array,
            ordered_category_names: List[str],
    ) -> pd.DataFrame:

        category_index_df = pd.DataFrame({
            'Category': self._get_string_categories(),
        }).reset_index().set_index('Category').loc[
            [str(x) for x in ordered_category_names]
        ].assign(
            Order=lambda df: np.arange(len(df))
        )

        mat = embeddings[:, category_index_df['index'].values]

        dists = []
        for i in range(mat.shape[1] - self.window_size):
            a = mat[:, list(range(max(0, i - self.window_size + 1), i + 1))].mean(axis=1)
            b = mat[:, list(range(i + 1, max(i + 1 + self.window_size, mat.shape[1])))].mean(axis=1)
            distance = self.distance_measure(a, b)
            dists.append(distance)

        category_index_df = category_index_df.assign(
            Dist=dists + [0] * self.window_size,
        ).sort_values(by='Dist', ascending=True)
        return category_index_df
