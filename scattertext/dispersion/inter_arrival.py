from copy import copy
from typing import Dict, Optional, Tuple, List, Callable, Union

import numpy as np
import pandas as pd
from scattertext.ParsedCorpus import ParsedCorpus
from spacy.tokens import Span
from tqdm.auto import tqdm

from scattertext.util import inherits_from
from scattertext.OffsetCorpus import OffsetCorpus


# from scattertext.dispersion.offset_inter_arrivals import corpus_to_concatenated_inter_arrivals


class InterArrivalCounts:
    def __init__(self, corpus: OffsetCorpus,
                 non_text: bool,
                 domains_to_preserve: Optional[List[str]] = None,
                 verbose: bool = False,
                 random_generator: Optional[np.random._generator.Generator] = None):
        self.corpus = corpus
        self.rng = random_generator
        self.domains_to_preserve = domains_to_preserve
        if not non_text:
            assert inherits_from(type(corpus), 'OffsetCorpus')
        self.term_inter_arrivals = {}
        self.term_category_inter_arrivals = {}
        self.__populate_inter_arrival_stats(verbose=verbose)

    def __populate_inter_arrival_stats(self, verbose: bool):
        it = enumerate(self.corpus.get_terms(use_metadata=True))
        if verbose:
            it = tqdm(it, total=self.corpus.get_num_metadata())
        for term_idx, term, in it:
            term_offsets = self.corpus.get_offsets()[term]
            interarrivals = []
            interarrival_cat = {}
            for doc_i, row in self.corpus.get_df().iterrows():
                cat = row[self.corpus.get_category_column()]
                doc = row[self.corpus.get_parsed_column()]
                last_end = None
                interarrival_cat.setdefault(cat, [])
                term_doc_offsets = term_offsets.get(doc_i, [])
                if term_doc_offsets:
                    for offset_start, offset_end in term_doc_offsets:
                        if self.__not_the_first_example_of_a_term(last_end):
                            intervening_token_count = self.__get_intervening_token_count(doc, last_end, offset_start)
                            self.__append_inter_arrival(cat, interarrival_cat, interarrivals, intervening_token_count)
                        last_end = offset_end
                    end_inter_arrival_tokens = self.__get_intervening_tokens_for_final_term(doc, term_doc_offsets)
                    self.__append_inter_arrival(cat, interarrival_cat, interarrivals, end_inter_arrival_tokens)

            self.term_inter_arrivals[term] = interarrivals
            self.term_category_inter_arrivals[term] = copy(interarrival_cat)

    def __get_intervening_tokens_for_final_term(self, doc, term_doc_offsets):
        tokens_before_first = doc.char_span(0, term_doc_offsets[0][0], alignment_mode='contract')
        token_count_before_first = 0 if tokens_before_first is None else len(tokens_before_first)
        tokens_after_last = doc.char_span(term_doc_offsets[-1][1], len(str(doc)), alignment_mode='contract')
        token_count_after_last = 0 if tokens_after_last is None else len(tokens_after_last)
        end_inter_arrival_tokens = token_count_before_first + token_count_after_last + 1
        return end_inter_arrival_tokens

    def __get_intervening_token_count(self, doc, last_end, offset_start):
        intervening_tokens = doc.char_span(last_end, offset_start, alignment_mode='contract')
        intervening_token_count = (0 if intervening_tokens is None else len(intervening_tokens)) + 1
        return intervening_token_count

    def __not_the_first_example_of_a_term(self, last_end: Optional[int]) -> bool:
        return last_end is not None

    def __append_inter_arrival(self,
                               cat: str,
                               interarrival_cat: Dict,
                               interarrivals,
                               intervening_token_count: int) -> None:
        interarrivals.append(intervening_token_count)
        interarrival_cat[cat].append(intervening_token_count)


def __get_sorted_doc_df(categories, corpus, domains_to_preserve, generator):
    doc_df = corpus.get_df()
    if categories is not None:
        doc_df = doc_df[lambda df: df[corpus.get_category_column()].isin(categories)]
    doc_df = doc_df.assign(
        _Order=lambda df: df.index if generator is None else generator.random(size=len(df)),
        _OriginalOrder=lambda df: np.arange(len(df))
    ).sort_values(
        by=([] if domains_to_preserve is None else domains_to_preserve) + ['_Order']
    )
    return doc_df


class WeibullInterArrivalStats:
    def __init__(
            self,
            inter_arrival_counts: InterArrivalCounts,
            verbose: bool = False,
            weibull_fit_func: Optional[Callable[[List[int]], object]] = None
    ):
        self.__register_weibull_fit_funct(weibull_fit_func)
        self.inter_arrival_counts = inter_arrival_counts
        data, data_cat = self.__collect_term_and_cat_data(inter_arrival_counts, verbose)
        self.term_df = pd.DataFrame(data).set_index('term')
        self.term_cat_df = pd.DataFrame(data_cat).set_index('term')

    def __register_weibull_fit_funct(self, weibull_fit_func):
        if weibull_fit_func is None:
            from reliability.Fitters import Fit_Weibull_2P
            self.weibull_fit_func = lambda failures: Fit_Weibull_2P(
                failures=failures,
                show_probability_plot=False,
                print_results=False
            )
        else:
            self.weibull_fit_func = weibull_fit_func

    def get_inter_arrival_times(self) -> pd.DataFrame:
        return self.term_df

    def get_category_specific_inter_arrival_times(self) -> pd.DataFrame:
        return self.term_cat_df

    def __collect_term_and_cat_data(self, inter_arrival_counts: InterArrivalCounts, verbose: bool) -> Tuple[List, List]:
        data = []
        data_cat = []
        it = self.__get_term_iterator(verbose)
        for term in it:
            if len(set(inter_arrival_counts.term_inter_arrivals[term])) > 1:
                fit = self.weibull_fit_func(inter_arrival_counts.term_inter_arrivals[term])
                data.append({'term': term, **self.__metrics_of_interest_from_fit(fit)})

                for cat, values in inter_arrival_counts.term_category_inter_arrivals[term].items():
                    if len(set(values)) > 1:
                        fit = self.weibull_fit_func(values)
                        data_cat.append({'term': term, 'Cat': cat, **self.__metrics_of_interest_from_fit(fit)})
        return data, data_cat

    def __metrics_of_interest_from_fit(self, fit):
        return {k: v for k, v in vars(fit).items()
                if k in ['alpha', 'alpha_upper', 'alpha_lower', 'beta', 'beta_upper',
                         'beta_lower', 'alpha_SE', 'beta_SE']}

    def __get_term_iterator(self, verbose):
        it = self.inter_arrival_counts.corpus.get_terms(use_metadata=True)
        if verbose:
            it = tqdm(it)
        return it
