from typing import Optional

import numpy as np

from scattertext.contextual_embeddings.running_stats_array import RunningStatsArray


class CorpusRunningStats:
    def __init__(self, corpus: 'TermDocMatrix', embedding_width: Optional[int] = None):
        self.corpus = corpus
        self.embedding_width = embedding_width
        self.term_stats = {}
        self.cat_stats = {}
        self.term_cat_stats = {}

    def add(self, term: str, cat: str, embedding: np.array, add_to_category_embeddings: bool) -> 'CorpusRunningStats':
        if self.embedding_width is None:
            self.embedding_width = len(embedding)
        if term in self.term_stats:
            self.term_stats[term].push(embedding)
        else:
            self.term_cat_stats[term] = {}
            self.term_stats[term] = self._get_fresh_running_stats().push(embedding)

        if add_to_category_embeddings:
            if cat in self.cat_stats:
                self.cat_stats[cat].push(embedding)
            else:
                self.cat_stats[cat] = self._get_fresh_running_stats().push(embedding)

        if cat not in self.term_cat_stats[term]:
            self.term_cat_stats[term][cat] = self._get_fresh_running_stats()

        self.term_cat_stats[term][cat].push(embedding)
        return self

    def add_embeddings_to_category(self, embeddings: np.array, cat: str) -> None:
        if len(embeddings):
            embedding = embeddings.mean(axis=0)
            if embedding.shape[0] == self.embedding_width and not np.any(np.isnan(embedding)):
                if cat in self.cat_stats:
                    self.cat_stats[cat].push(embedding)
                else:
                    self.cat_stats[cat] = self._get_fresh_running_stats().push(embedding)

    def _get_fresh_running_stats(self) -> RunningStatsArray:
        return RunningStatsArray(self.embedding_width)

    def get_term_category_stats(self, term: str, cat: str) -> Optional[RunningStatsArray]:
        return self.term_cat_stats.get(term, {}).get(cat, None)

    def get_category_stats(self, cat: str) -> Optional[RunningStatsArray]:
        return self.cat_stats.get(cat, None)

    def get_term_stats(self, cat: str) -> Optional[RunningStatsArray]:
        return self.term_stats.get(cat, None)
