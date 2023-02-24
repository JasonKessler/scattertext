import abc
from typing import Dict, Optional

import pandas as pd
import numpy as np
from scattertext.termscoring.RankDifferenceScorer import RankDifferenceScorer

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer

from scattertext.all_category_scorers.all_category_scorer import AllCategoryScorer


class AllCategoryTermScorer(AllCategoryScorer):
    def _free_init(self, **kwargs):
        self.term_scorer_factory_: type = kwargs.get('term_scorer', RankDifferenceScorer)
        self.term_scorer_kwargs_: Dict = kwargs.get('term_scorer_kwargs', {})

    def set_corpus(self, corpus: Optional) -> 'AllCategoryScorer':
        AllCategoryScorer.set_corpus(self, corpus=corpus)
        self.term_scorer_ = None
        if self.corpus_ is not None:
            self.term_scorer_: CorpusBasedTermScorer = self.term_scorer_factory_(
                self.corpus_,
                **self.term_scorer_kwargs_ if self.term_scorer_kwargs_ is not None else {}
            )
        return self

    def get_rank_freq_df(self) -> pd.DataFrame:
        if self.term_scorer_ is None:
            raise Exception("Ensure the corpus has been set.")
        # freq_df = self.term_ranker_.use_non_text_features(self.non_text_).get_ranks(label_append='')
        freq_df = self.term_ranker_.set_non_text(self.non_text_).get_ranks(label_append='')
        if self.non_text_:
            self.term_scorer_ = self.term_scorer_.use_metadata()
        dfs = []
        for category in self.corpus_.get_categories():
            cat_df = pd.DataFrame({
                'Score': self.term_scorer_.set_categories(str(category)).get_scores().sort_values(ascending=False),
                'Category': category,
            })
            cat_df.index = cat_df.index.rename('Term')
            cat_df = cat_df.reset_index().assign(
                Rank=lambda df: np.arange(len(df), dtype=int),
                Frequency=lambda df: freq_df.loc[df.Term.values, str(category)].values
            )
            dfs.append(cat_df)

        return pd.concat(dfs).reset_index(drop=True)

    def get_score_df(self, score_append=' Score', freq_append=' Freq') -> pd.DataFrame:
        rank_df = self.term_ranker_.get_ranks(label_append=freq_append)
        for category in self.corpus_.get_categories():
            scores = self.term_scorer_.set_categories(category_name=category).get_scores()
            rank_df[category + score_append] = scores
        return rank_df[sorted(rank_df.columns)]
