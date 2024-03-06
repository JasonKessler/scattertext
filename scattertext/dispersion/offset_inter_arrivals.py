from typing import Optional, List, Dict, Callable

import pandas as pd
import spacy
import numpy as np
from tqdm.auto import tqdm

from scattertext.util import inherits_from
from scattertext.OffsetCorpus import OffsetCorpus


def offset_corpus_to_concatenated_inter_arrivals(
        corpus: OffsetCorpus,
        categories: Optional[List[str]] = None,
        generator: Optional[np.random._generator.Generator] = None,
        domains_to_preserve: Optional[List[str]] = None,
        join_text: str = '\n',
        verbose: bool = False,
        nlp: Optional[spacy.language.Language] = None
) -> Dict[str, List[int]]:
    if not isinstance(corpus, OffsetCorpus):
        raise Exception(f"The corpus argument was of type {type(corpus)}. "
                        f"Use offset_corpus_to_concatenated_inter_arrivals instead.")

    doc_df = __order_docs_to_concat(categories, corpus, domains_to_preserve, generator, join_text)
    doc = __concatenate_doc(corpus, doc_df, join_text, nlp)
    doc_id_to_offset = dict(doc_df[['_OrigIdx', 'StartOffset']].set_index('_OrigIdx')['StartOffset'])

    term_inter_arrivals = {}
    it = corpus.get_offsets().items()
    if verbose:
        it = tqdm(it, total=len(corpus.get_offsets()))
    for term, doc_offsets in it:
        new_offsets = _translate_offsets_to_concatenated_doc(doc_id_to_offset, doc_offsets)
        term_inter_arrivals[term] = _collect_term_inter_arrivals_on_concatenated_doc(doc, new_offsets)
    return term_inter_arrivals


def category_specific_inter_arrivals_from_offset_corpus(
        corpus: OffsetCorpus,
        weibull_fit_func: Optional[Callable] = None,
        verbose: bool = False,
) -> pd.DataFrame:
    if not isinstance(corpus, OffsetCorpus):
        raise Exception(f"The corpus argument was of type {type(corpus)}. "
                        f"Use offset_corpus_to_concatenated_inter_arrivals instead.")

    if weibull_fit_func is None:
        from reliability.Fitters import Fit_Weibull_2P
        weibull_fit_func = lambda failures: Fit_Weibull_2P(
            failures=failures,
            show_probability_plot=False,
            print_results=False
        )

    cat_term_ias = {cat: offset_corpus_to_concatenated_inter_arrivals(
        corpus,
        categories=[cat],
        verbose=verbose
    ) for cat in corpus.get_categories()}

    data = []
    for cat, term_ias in cat_term_ias.items():
        for term, ias in tqdm(term_ias.items()):
            if len(ias) > 1:
                data.append({'term': term, 'cat': cat, 'freq': len(ias),
                             **__get_term_stats(ias, weibull_fit_func)})
    return pd.DataFrame(data)


def __get_term_stats(ias, weibull_fit_func):
    fit = weibull_fit_func(ias)
    return {k: v for k, v in vars(fit).items()
                  if k in ['alpha', 'alpha_upper', 'alpha_lower', 'beta', 'beta_upper',
                           'beta_lower', 'alpha_SE', 'beta_SE']}


def __concatenate_doc(corpus, doc_df, join_text, nlp):
    doc_str = join_text.join(doc_df[corpus.get_parsed_column()].apply(str))
    if nlp is None:
        nlp = spacy.blank('en')
    doc = nlp(doc_str)
    return doc


def __order_docs_to_concat(categories, corpus, domains_to_preserve, generator, join_text):
    doc_df = corpus.get_df().assign(
        _OrigIdx=lambda df: np.arange(len(df)).astype(int)
    )
    if categories is not None:
        doc_df = doc_df[lambda df: df[corpus.get_category_column()].isin(categories)]
    doc_df = doc_df.assign(
        _Order=lambda df: df.index if generator is None else generator.random(size=len(df)),
        _Len=lambda df: df[corpus.get_parsed_column()].apply(str).apply(len),
    ).sort_values(
        by=([] if domains_to_preserve is None else domains_to_preserve + ['_Order'])
    ).assign(
        StartOffset=lambda df: (df._Len + len(join_text)).shift(1).cumsum().fillna(0)
    )
    return doc_df


def _collect_term_inter_arrivals_on_concatenated_doc(doc, new_offsets):
    num_tokens_before_first = None
    last_end = 0
    inter_arrivals = []
    for offset_i, (start_offset, end_offset) in enumerate(new_offsets):
        tokens = doc.char_span(last_end, start_offset, alignment_mode='contract')
        if tokens is None:
            tokens = []
        num_tokens_in_between = len(tokens)
        if num_tokens_in_between == 0:
            num_tokens_in_between = 1
        if offset_i == 0:
            num_tokens_before_first = num_tokens_in_between
        else:
            inter_arrivals.append(num_tokens_in_between)
        last_end = end_offset

    if num_tokens_before_first is not None:
        tokens = doc.char_span(last_end, len(str(doc)), alignment_mode='contract')
        if tokens is None:
            tokens = []

        last_token_count = num_tokens_before_first + len(tokens)
        if last_token_count is 0: last_token_count = 1
        inter_arrivals.append(last_token_count)
    return inter_arrivals


def _translate_offsets_to_concatenated_doc(doc_id_to_offset, doc_offsets):
    new_offsets = []
    for orig_doc_idx, offsets in doc_offsets.items():
        doc_offset = doc_id_to_offset.get(orig_doc_idx, None)
        if doc_offset is not None:
            for offset in offsets:
                new_offsets.append((offset[0] + doc_offset, offset[1] + doc_offset))
    new_offsets.sort()
    return new_offsets
