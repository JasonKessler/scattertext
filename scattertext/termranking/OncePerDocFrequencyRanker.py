import pandas as pd

from scattertext.termranking.TermRanker import TermRanker


class OncePerDocFrequencyRanker(TermRanker):
	def get_ranks(self):
		mat = self._term_doc_matrix.get_term_count_mat()
		return pd.DataFrame(mat,
		                    index=pd.Series(self._term_doc_matrix.get_terms(), name='term'),
		                    columns=[c + ' freq' for c
		                             in self._term_doc_matrix.get_categories()])
