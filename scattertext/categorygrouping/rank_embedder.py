from abc import ABCMeta
from typing import Optional, Callable, Dict

import numpy as np
import pandas as pd

from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer
from scattertext.categorygrouping.characteristic_embedder_base import CategoryEmbedderABC
from scattertext.util import inherits_from

class RankEmbedder(CategoryEmbedderABC):
    def __init__(self,
                 scorer_function: Optional[Callable[[np.array, np.array], np.array]] = None,
                 term_scorer: Optional[CorpusBasedTermScorer] = None,
                 rank_threshold: int = 10,
                 term_scorer_kwargs: Optional[Dict] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scorer_function = RankDifference().get_scores if scorer_function is None else scorer_function
        self.term_scorer = term_scorer
        self.rank_threshold = rank_threshold
        self.term_scorer_kwargs = {} if term_scorer_kwargs is None else term_scorer_kwargs

    def embed_categories(self, corpus: TermDocMatrix, non_text: bool = False) -> np.array:
        tdf = corpus.get_freq_df(use_metadata=non_text, label_append='')
        term_freqs = tdf.sum(axis=1)
        score_df = pd.DataFrame({
            category: pd.Series(
                self.__get_scores_for_category(str(category), tdf, term_freqs, non_text, corpus),
                index=corpus.get_terms(use_metadata=non_text)
            ).sort_values(ascending=False).head(self.rank_threshold)
            for category in corpus.get_categories()
        })
        return score_df.fillna(0).T.values

    def __get_scores_for_category(self, category, tdf, term_freqs, non_text, corpus):
        if self.term_scorer is not None:
            if inherits_from(self.term_scorer, 'CorpusBasedTermScorer') and type(self.term_scorer) == ABCMeta:
                scorer = self.term_scorer(corpus, **self.term_scorer_kwargs)
            else:
                scorer = self.term_scorer
            if non_text:
                scorer = scorer.use_metadata()
            scorer = scorer.set_categories(category_name=category)
            return scorer.get_scores()
        return self.scorer_function(tdf[str(category)], term_freqs - tdf[str(category)])
