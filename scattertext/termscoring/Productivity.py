import pandas as pd
import numpy as np
from scattertext.TermDocMatrixWithoutCategories import TermDocMatrixWithoutCategories

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


def whole_corpus_productivity_scores(tdm: TermDocMatrixWithoutCategories) -> pd.DataFrame:
    term_freqs = pd.Series(tdm.get_term_freqs(), index=tdm.get_terms())
    ngrams_mask = [' ' in x for x in tdm.get_terms()]

    data = []
    for ngram, ngram_freq in term_freqs[ngrams_mask].items():
        for term in ngram.split():
            try:
                tdm.get_term_index(term)
            except KeyError:
                continue
            data.append([tdm.get_term_index(term), ngram_freq])

    ngram_freq_df = pd.DataFrame(data, columns=['TermIndex', 'NgramFreq'])

    productivity_df = pd.merge(
        ngram_freq_df,
        ngram_freq_df.groupby(
            ['TermIndex']
        ).sum().rename(
            columns={'NgramFreq': 'TermCatFreq'}
        ).reset_index(),
        on=['TermIndex']
    ).assign(
        P=lambda df: df.NgramFreq / df.TermCatFreq
    ).dropna().groupby(['TermIndex']).apply(
        lambda df: -np.sum(df.P * np.log(df.P) / np.log(2))
    ).reset_index().rename(
        columns={0: 'Productivity'}
    ).assign(
        Term = lambda df: np.array(tdm.get_terms())[df.TermIndex],
        Frequency = lambda df: term_freqs.loc[df.Term.values].values
    )[lambda df: [c for c in df.columns if c != 'TermIndex']].set_index('Term')
    return productivity_df


class ProductivityScorer(CorpusBasedTermScorer):
    '''
    Citation: Anne-Kathrin Schumann. 2016. Brave new world: Uncovering topical dynamics in the ACL Anthology
    reference corpus using term life cycle information. In Proceedings of the 10th SIGHUM Workshop on Language Technology for Cultural Heritage, Social Sciences, and Humanities, pages 1–11, Berlin, Germany. Association for Computational Linguistics.


    term_scorer = (MannWhitneyU(corpus).set_categories('Positive', ['Negative'], ['Plot']))

    html = st.produce_frequency_explorer(
        corpus,
        category='Positive',
        not_categories=['Negative'],
        neutral_categories=['Plot'],
        term_scorer=term_scorer,
        metadata=rdf['movie_name'],
        grey_threshold=0,
        show_neutral=True
    )
    file_name = 'rotten_fresh_mwu.html'
    open(file_name, 'wb').write(html.encode('utf-8'))
    IFrame(src=file_name, width=1300, height=700)
    '''

    def _set_scorer_args(self, **kwargs):
        pass

    def get_scores(self, *args):
        return self.get_score_df()['Productivity']

    def get_score_df(self) -> pd.DataFrame:
        '''
        Computes Schumann (2016) term productivity scores. Requires corpus to have both unigrams and ngrams. Corpus
        should not be compacted.
        '''
        term_freq_df = self.corpus_.get_term_freq_df('')
        ngrams_mask = [' ' in x for x in self.corpus_.get_terms()]

        data = []
        for ngram, ngram_freqs in term_freq_df[ngrams_mask].iterrows():
            for term in ngram.split():
                term_index = self.corpus_.get_term_index(term)
                for category_index, ngram_freq in enumerate(ngram_freqs):
                    data.append([term_index, category_index, ngram_freq])

        ngram_freq_df = pd.DataFrame(data, columns=['TermIndex', 'CategoryIndex', 'NgramFreq'])

        productivity_df = pd.merge(
            ngram_freq_df,
            ngram_freq_df.groupby(
                ['TermIndex', 'CategoryIndex']
            ).sum().rename(
                columns={'NgramFreq': 'TermCatFreq'}
            ).reset_index(),
            on=['TermIndex', 'CategoryIndex']
        ).assign(
            P=lambda df: df.NgramFreq / df.TermCatFreq
        ).dropna().groupby(['TermIndex', 'CategoryIndex']).apply(
            lambda df: -np.sum(df.P * np.log(df.P) / np.log(2))
        ).reset_index().rename(
            columns={0: 'Productivity'}
        )

        return pd.pivot_table(
            productivity_df.assign(
                Term=lambda df: np.array(self.corpus_.get_terms())[df.TermIndex],
                Category=lambda df: np.array(self.corpus_.get_categories())[df.CategoryIndex],
            ),
            index='Term',
            columns='Category',
            values='Productivity'
        ).fillna(0).assign(
            Delta=lambda df: df[self.category_name] - df[self.not_category_names].mean(axis=1)
        )

    def get_scores(self, *args) -> pd.Series:
        return self.get_score_df()['Delta']

    def get_name(self) -> str:
        return "Delta Productivity"
