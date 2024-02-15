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
        if scorer is None:
            scorer = RankDifference()
        if ranker is None:
            ranker = AbsoluteFrequencyRanker(self.corpus)
        if inherits_from(ranker, 'TermRanker'):
            ranker = ranker(self.corpus)
        if self.use_metadata:
            ranker = ranker.use_non_text_features()
        data = []
        it = self.corpus.get_categories()
        if verbose:
            it = tqdm(it)
        for cat in it:
            scores = self.__get_scores(cat=cat, scorer=scorer, ranker=ranker)
            for term_rank, (term, score) in enumerate(scores.sort_values(ascending=False).items()):
                data.append({'Category': cat, 'Term': term, 'Rank': term_rank, 'Score': score})

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
        cat_freq = term_freq_df[cat]
        global_freq = term_freq_df.sum(axis=1)
        return scorer.get_scores(cat_freq, global_freq - cat_freq)
