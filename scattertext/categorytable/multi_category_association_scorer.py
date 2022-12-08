import pandas as pd
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer

from scattertext import RankDifference, AbsoluteFrequencyRanker
from scattertext.categorytable import MultiCategoryAssociationBase
from scattertext.termranking.TermRanker import TermRanker


class MultiCategoryAssociationScorer(MultiCategoryAssociationBase):
    def get_category_association(self, ranker: TermRanker = None, scorer=None):
        if scorer is None:
            scorer = RankDifference()
        if ranker is None:
            ranker = AbsoluteFrequencyRanker(self.corpus)
        if self.use_metadata:
            ranker = ranker.use_non_text_features()
        data = []
        for cat in self.corpus.get_categories():
            scores = self.__get_scores(cat=cat, scorer=scorer, ranker=ranker)
            for term_rank, (term, score) in enumerate(scores.sort_values(ascending=False).items()):
                data.append({'Category': cat, 'Term': term, 'Rank': term_rank, 'Score': score})

        return pd.DataFrame(data).groupby('Rank')

    def __get_scores(self, cat, scorer, ranker) -> pd.Series:
        if isinstance(scorer, CorpusBasedTermScorer):
            scorer = scorer.set_categories(category_name=cat).set_term_ranker(term_ranker=ranker)
            if self.use_metadata:
                scorer = scorer.use_metadata()
            return scorer.get_scores()

        term_freq_df = ranker.get_ranks('')
        cat_freq = term_freq_df[cat]
        global_freq = term_freq_df.sum(axis=1)
        return scorer.get_scores(cat_freq, global_freq - cat_freq)
