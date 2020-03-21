import pandas as pd

from scattertext.termranking.TermRanker import TermRanker


class OncePerDocFrequencyRanker(TermRanker):
	def get_ranks(self, label_append=' freq'):
		mat = self._term_doc_matrix.get_term_count_mat()
		return self.get_ranks_from_mat(mat, label_append)

	def get_ranks_from_mat(self, mat, label_append=' freq'):
		return pd.DataFrame(mat,
							index=pd.Series(self._term_doc_matrix.get_terms(), name='term'),
							columns=[str(c) + label_append for c
									 in self._term_doc_matrix.get_categories()])
