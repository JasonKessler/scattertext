import pandas as pd

from scattertext.termranking.TermRanker import TermRanker


class OncePerDocFrequencyRanker(TermRanker):
    def get_ranks(self, label_append=' freq'):
        mat = self._corpus.get_term_count_mat(non_text=self._use_non_text_features)
        return self.get_ranks_from_mat(mat, label_append)

    def get_ranks_from_mat(self, mat, label_append=' freq'):
        return pd.DataFrame(
            mat,
            index=pd.Series(self._corpus.get_terms(use_metadata=self._use_non_text_features), name='term'),
            columns=[str(c) + label_append for c in self._corpus.get_categories()]
        )
