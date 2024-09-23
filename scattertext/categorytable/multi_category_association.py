from scattertext.termranking import AbsoluteFrequencyRanker

from scattertext.util import inherits_from

from scattertext.termscoring.RankDifference import RankDifference


class MultiCategoryAssociationBase:
    def __init__(
            self,
            corpus,
            use_metadata=False,
            non_text=False,
            use_non_text_features=False,
            ranker=None,
            scorer=None
    ):
        self.corpus = corpus
        self.use_metadata = use_metadata or non_text or use_non_text_features
        self.ranker, self.scorer = self._resolve_ranker_and_scorer(ranker=ranker, scorer=scorer)

    def get_category_association(self, **kwargs):
        raise NotImplementedError()

    def get_category_association_and_freqs(self, **kwargs):
        raise NotImplementedError()


    def _resolve_ranker_and_scorer(self, ranker, scorer):
        if scorer is None:
            scorer = RankDifference()
        if inherits_from(scorer, 'CorpusBasedTermScorer'):
            scorer = scorer(self.corpus, use_metadata=self.use_metadata)
        elif type(scorer) == type:
            scorer = scorer()
        if ranker is None:
            ranker = AbsoluteFrequencyRanker(self.corpus)
        if inherits_from(ranker, 'TermRanker'):
            ranker = ranker(self.corpus)
        if self.use_metadata:
            ranker = ranker.use_non_text_features()
        return ranker, scorer