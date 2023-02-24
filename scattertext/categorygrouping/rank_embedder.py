from typing import Optional, Callable

import numpy as np
import pandas as pd

from scattertext import RankDifference, TermDocMatrix, CorpusBasedTermScorer
from scattertext.categorygrouping.characteristic_embedder_base import CategoryEmbedderABC


class RankEmbedder(CategoryEmbedderABC):
    def __init__(self,
                 scorer_function: Optional[Callable[[np.array, np.array], np.array]] = None,
                 term_scorer: Optional[CorpusBasedTermScorer] = None,
                 rank_threshold: int = 10,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scorer_function = RankDifference().get_scores if scorer_function is None else scorer_function
        self.term_scorer = term_scorer
        self.rank_threshold = rank_threshold

    def embed_categories(self, corpus: TermDocMatrix, non_text: bool = False) -> np.array:
        tdf = corpus.get_freq_df(use_metadata=non_text, label_append='')
        term_freqs = tdf.sum(axis=1)
        score_df = pd.DataFrame({
            category: pd.Series(
                self.__get_scores_for_category(str(category), tdf, term_freqs, non_text),
                index=corpus.get_terms(use_metadata=non_text)
            ).sort_values(ascending=False).head(self.rank_threshold)
            for category in corpus.get_categories()
        })
        return score_df.fillna(0).T.values

    def __get_scores_for_category(self, category, tdf, term_freqs, non_text):
        if self.term_scorer is not None:
            scorer = self.term_scorer.set_categories(category_name=category)
            if non_text:
                scorer = scorer.use_metadata()
            return scorer.get_scores()
        return self.scorer_function(tdf[str(category)], term_freqs - tdf[str(category)])
