from typing import Optional, Callable, Type
import numpy as np
import pandas as pd
from scattertext.termranking.TermRanker import TermRanker
from scipy.sparse import csr_matrix



def tfidf_ranker_factory(
        scale_tf: Optional[Callable[[np.array], np.array]] = None,
) -> Type['TermRanker']:
    if scale_tf is None:
        scale_tf = np.sqrt


    class tfidf_ranker(TermRanker):
        def get_ranks(self, label_append: str = ' freq') -> pd.DataFrame:
            tdm = self.get_term_doc_mat()
            sqrt_tf = scale_tf(tdm)
            idf = np.log(self._corpus.get_num_docs() / (tdm > 0).sum(axis=0).A1)
            tfidf = sqrt_tf.multiply(idf).tocsr()
            y = self._corpus.get_category_ids()
            for cat_i, cat in enumerate(self._corpus.get_categories()):
                tfidf[y == cat_i, :].mean(axis=0).A1
                cat + label_append
            rank_df = pd.DataFrame(
                {
                    cat + label_append: tfidf[y == cat_i, :].mean(axis=0).A1
                    for cat_i, cat
                    in enumerate(self._corpus.get_categories())
                }
            )
            rank_df['term'] = self.get_terms()
            return rank_df.set_index('term')

    return tfidf_ranker