from typing import Optional, Callable, List

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

tqdm.pandas()

from scattertext.termranking.TermRanker import TermRanker
from scattertext.termranking.AbsoluteFrequencyRanker import AbsoluteFrequencyRanker


class NPMICompactor(object):
    def __init__(
            self,
            term_ranker: type = AbsoluteFrequencyRanker,
            minimum_term_count: int = 2,
            number_terms_per_length: int = 2000,
            token_split_function: Optional[Callable[[str], List[str]]] = None,
            token_join_function: Optional[Callable[[List[str]], str]] = None,
            show_progress: bool = True
    ):
        '''

        Parameters
        ----------
        term_ranker : TermRanker
            Default AbsoluteFrequencyRanker
        minimum_term_count : int
            Default 2
        number_terms_per_length : int
            Select X top PMI terms per ngram length
            Default 2000
        token_split_function: Optional[Callable[[str], List[str]]] = None
            Splits a term into ngrams, default lambda x: x.split()
        token_join_function: Optional[Callable[[List[str]], str]] = None
            Joins a sequence of tokens int a string, opposite of split function, default lambda x: x.join(' ')
        show_progress : bool
            Shows TQDM for PMI filtering


        '''
        self.term_ranker = term_ranker
        self.minimum_term_count = minimum_term_count
        self.number_terms_per_length = number_terms_per_length
        self.show_progress = show_progress
        self.token_split_function = (lambda x: x.split()) if token_split_function is None else token_split_function
        self.token_join_function = (lambda x: ' '.join(x)) if token_join_function is None else token_join_function

    def compact(self, term_doc_matrix, non_text=False):
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
        pmi_df = self.get_pmi_df(term_doc_matrix, non_text)

        threshold_df = self._get_ngram_length_pmi_thresholds(pmi_df)

        filtered_pmi_df = pd.merge(
            pmi_df,
            threshold_df,
            left_on='Len',
            right_index=True
        )[lambda df: df.NPMI < df.NPMIThreshold]

        terms_to_remove = list(filtered_pmi_df.Term)

        return term_doc_matrix.remove_terms(
            terms_to_remove, non_text
        ).remove_infrequent_words(
            self.minimum_term_count - 1, term_ranker=self.term_ranker, non_text=non_text
        )

    def get_pmi_df(self, term_doc_matrix, non_text: bool = False):
        freqs = self._get_term_frequencies(non_text, term_doc_matrix)
        pmi_df = self._get_pmi_df(freqs)[
            lambda df: df.Count >= self.minimum_term_count
        ]
        return pmi_df

    def _get_term_frequencies(self, non_text, term_doc_matrix):
        ranker = self.term_ranker(term_doc_matrix)
        if non_text:
            ranker = ranker.use_non_text_features()
        freqs = ranker.get_ranks().sum(axis=1)
        return freqs

    def _get_ngram_length_pmi_thresholds(self, pmi_df: pd.DataFrame) -> pd.DataFrame:
        return pmi_df[lambda df: (df.Len > 1) & (df.Count >= self.minimum_term_count)].groupby(
            'Len'
        ).apply(
            lambda gdf: pd.Series({'NPMI': 0}) if len(gdf) <= self.number_terms_per_length else gdf.sort_values(
                by='NPMI', ascending=False
            ).iloc[self.number_terms_per_length][['NPMI']]
        ).rename(columns={'NPMI': 'NPMIThreshold'})

    def _get_pmi_df(self, freqs: pd.Series) -> pd.DataFrame:
        # ngram_lens = np.array([len(x.split()) for x in freqs.index])
        wc = dict(pd.DataFrame({
            'Len': [len(x.split()) for x in freqs.index],
            'Freq': freqs
        }).groupby('Len').sum()['Freq'])

        backoff = freqs.mean()

        def prob(ngram):
            if len(ngram) == 0:
                return 1

            joined_ngram = self.token_join_function(ngram)
            if joined_ngram in freqs:
                return freqs.loc[joined_ngram] / (wc[len(ngram)] - len(ngram) + 1)

            if ngram[0] in freqs.index:
                return freqs.loc[ngram[0]] / wc[1] * prob(ngram[1:])

            return backoff / wc[1] * prob(ngram[1:])

        apply = lambda df: df.apply
        if self.show_progress:
            apply = lambda df: df.progress_apply

        return pd.DataFrame({'Count': freqs}).reset_index(
        ).rename(
            columns={'term': 'Term'}
        ).assign(
            Len=lambda df: df.Term.apply(lambda x: len(self.token_split_function(x))),
        )[lambda df: df.Len > 1].assign(
            WholeProb=lambda df: apply(df.Term)(lambda x: prob(self.token_split_function(x))),
            UniProb=lambda df: apply(df.Term)(
                lambda x: np.exp(sum(np.log(prob([tok])) for tok in self.token_split_function(x)))),
            PMI=lambda df: np.log(df.WholeProb) - np.log(df.UniProb),
            NPMI=lambda df: -df.PMI / np.log(df.WholeProb)
        )
