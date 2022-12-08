import abc
from typing import Optional, Dict

import pandas as pd

from scattertext.termranking.AbsoluteFrequencyRanker import AbsoluteFrequencyRanker
from scattertext.termranking.TermRanker import TermRanker


class AllCategoryScorer(abc.ABC):
    def __init__(
            self,
            corpus = Optional,
            non_text: bool = False,
            term_ranker: type = AbsoluteFrequencyRanker,
            term_ranker_kwargs: Optional[Dict] = None,
            **kwargs
    ):
        self.term_ranker_kwargs_ = term_ranker_kwargs
        self.term_ranker_factory_ = term_ranker
        self.set_non_text(non_text)
        self._free_init(**kwargs)
        self.set_corpus(corpus)

    def set_corpus(self, corpus: Optional) -> 'AllCategoryScorer':
        self.corpus_ = corpus
        if corpus is None:
            self.term_ranker_ = None
        else:
            self.term_ranker_: Optional[TermRanker] = self.term_ranker_factory_(
                corpus,
                **self.term_ranker_kwargs_ if self.term_ranker_kwargs_ is not None else {}
            )
        return self

    def set_non_text(self, non_text: bool) -> 'AllCategoryScorer':
        self.non_text_ = non_text
        return self

    def _free_init(self, **kwargs):
        pass

    @abc.abstractmethod
    def get_rank_freq_df(self) -> pd.DataFrame:
        raise NotImplementedError()

    def get_score_df(self, score_append=' Score', freq_append=' Freq') -> pd.DataFrame:
        df = pd.pivot_table(
            self.get_rank_freq_df(),
            index='Term',
            values=['Score', 'Frequency'],
            columns=['Category']
        )

        df.columns = [category + {'Score': score_append, 'Frequency': freq_append}[metric_type]
                      for metric_type, category in df.columns.to_flat_index()]
        return df[lambda df: list(sorted(df.columns))]


