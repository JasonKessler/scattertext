import abc

import pandas as pd
from tqdm.auto import tqdm

from scattertext.TermDocMatrixWithoutCategories import TermDocMatrixWithoutCategories
from scattertext.features.featoffsets.flexible_ngram_features import sequence_window
from scattertext.termranking import AbsoluteFrequencyRanker


class BaseTermCompactor(abc.ABC):
    @abc.abstractmethod
    def compact(self, term_doc_matrix: TermDocMatrixWithoutCategories, non_text:bool=False):
        '''
        Parameters
        ----------
        term_doc_matrix : TermDocMatrix
            Term document matrix object to compact
        non_text : bool
            Use non-text features instead of terms

        Returns
        -------
        New term doc matrix
        '''
        pass

class NgramPercentageCompactor(BaseTermCompactor):
    def __init__(
            self,
            term_ranker: type = AbsoluteFrequencyRanker,
            minimum_term_count: int = 0,
            usage_portion: float = 0.7,
            verbose: bool = False
    ):
        '''

        Parameters
        ----------
        term_ranker : TermRanker
            Default AbsoluteFrequencyRanker
        minimum_term_count : int
            Default 0
        usage_portion : float
            Portion of times term is used in a containing n-gram for it to be eliminated
            Default 0.8
        verbose : bool
            Show progress bar
        '''
        self.term_ranker = term_ranker
        self.minimum_term_count = minimum_term_count
        self.usage_portion = usage_portion
        self.verbose = verbose

    def compact(self, term_doc_matrix, non_text=False):
        elim_df = self.get_elimination_df(term_doc_matrix, non_text)
        if self.verbose:
            print(f"Ngram percentage compactor removed {len(elim_df)} terms.")

        return term_doc_matrix.remove_terms(
            terms=elim_df.Eliminations,
            ignore_absences=True,
            non_text=non_text
        )

    def get_elimination_df(self, term_doc_matrix, non_text = False) -> pd.DataFrame:
        freq_df = pd.DataFrame({
            'Count': self.term_ranker(term_doc_matrix).set_non_text(non_text).get_ranks().sum(axis=1),
        })[
            lambda df: df.Count >= self.minimum_term_count
        ]
        max_subgramsize = max(len(tok.split()) for tok in freq_df.index) - 1
        eliminations = []
        eliminators = []
        it = freq_df.iterrows()
        if self.verbose:
            it = tqdm(freq_df.iterrows(), total=len(freq_df))
        for row_i, row in it:
            toks = row.name.split()
            gram_len = len(toks)
            if gram_len > 1:
                subgrams = []
                for i in range(min(max_subgramsize, gram_len - 1), 0, -1):
                    for subtoks in sequence_window(toks, i):
                        subgrams.append(' '.join(subtoks))
                found_subgrams = freq_df.index.intersection(subgrams)
                to_elim = list(freq_df.loc[
                                   found_subgrams
                               ][lambda df: row.Count > df.Count * self.usage_portion].index)
                if to_elim:
                    #print(to_elim)
                    eliminations += to_elim
                    eliminators += [row.name] * len(to_elim)
        return pd.DataFrame({'Eliminations': eliminations, 'Eliminators': eliminators})

