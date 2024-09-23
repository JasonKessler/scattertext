from typing import Type, Union

import pandas as pd
from tqdm.auto import tqdm

from scattertext import inherits_from
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer
from scattertext.categorytable import MultiCategoryAssociationBase
from scattertext.termranking.TermRanker import TermRanker


class MultiCategoryAssociationScorer(MultiCategoryAssociationBase):
    def get_category_association(self, ranker: Union[TermRanker, Type] = None, scorer=None, verbose=False):
        ranker, scorer = self._resolve_ranker_and_scorer(ranker, scorer)
        data = []
        it = self.corpus.get_categories()
        if verbose:
            it = tqdm(it)
        for cat in it:
            scores = self.__get_scores(cat=cat, scorer=scorer, ranker=ranker)
            for term_rank, (term, score) in enumerate(scores.sort_values(ascending=False).items()):
                data.append({'Category': cat, 'Term': term, 'Rank': term_rank, 'Score': score})

        return pd.DataFrame(data)

    def get_category_association_and_freqs(self, ranker: Union[TermRanker, Type] = None, scorer=None, verbose=False):
        ranker, scorer = self._resolve_ranker_and_scorer(ranker, scorer)
        data = []
        it = self.corpus.get_categories()
        if verbose:
            it = tqdm(it)
        term_freq_df = ranker.get_ranks('')
        for cat in it:
            scores = self.__get_scores(cat=cat, scorer=scorer, ranker=ranker)
            freqs = term_freq_df[str(cat)]
            for term_rank, (term, score) in enumerate(scores.sort_values(ascending=False).items()):
                data.append({'Category': cat,
                             'Term': term,
                             'Freq': freqs.loc[term],
                             'Rank': term_rank,
                             'Score': score})

        return pd.DataFrame(data)


    def __get_scores(self, cat, scorer, ranker) -> pd.Series:
        if inherits_from(type(scorer), 'CorpusBasedTermScorer'):
            if self.use_metadata:
                scorer = scorer.use_metadata()
            scorer = scorer.set_categories(category_name=cat)
            if ranker is not None:
                scorer = scorer.set_term_ranker(term_ranker=ranker)
            return scorer.get_scores()
        term_freq_df = ranker.get_ranks('')
        try:
            cat_freq = term_freq_df[cat]
        except KeyError:
            cat_freq = term_freq_df[str(cat)]

        global_freq = term_freq_df.sum(axis=1)
        return scorer.get_scores(cat_freq, global_freq - cat_freq)
