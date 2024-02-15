from typing import Optional, Callable, List, Union

import numpy as np
import pandas as pd
from scattertext.TermDocMatrixWithoutCategories import TermDocMatrixWithoutCategories

from scattertext.termranking import AbsoluteFrequencyRanker
from scipy.sparse import csc_matrix, csr_matrix, vstack, hstack
from sklearn.preprocessing import StandardScaler

from scattertext.smoothing.lowess import Lowess
from scattertext.termranking.TermRanker import TermRanker
from scattertext.TermDocMatrix import TermDocMatrix


class Dispersion(object):
    def __init__(
            self,
            corpus: Optional[TermDocMatrixWithoutCategories] = None,
            term_doc_mat: Optional[np.matrix] = None,
            non_text=False,
            use_categories_as_documents=False,
            tqdm=None,
            regressor=None,
            term_ranker: Optional[TermRanker] = None,
            vocabulary: Optional[List[str]] = None,
            add_smoothing_part: bool = False
    ):
        """
        corpus, Optional ]TermDocMatrix type-object; if not present, pass an argument to the `term_doc_mat` parameter
        term_doc_mat, Optional[np.matrix]; use this term doc matrix
        non_text bool, default False; use metadata features
        use_categories_as_document, bool, default False; use categories in lieu of documents
        add_smoothing_part: add a part containing one of every terms

        From https://www.researchgate.net/publication/332120488_Analyzing_dispersion
        Stefan Th. Gries. Analyzing dispersion. April 2019. Practical handbook of corpus linguistics. Springer.

        Parts are considered documents, unless use_categories is True. Then categories are treated as parts.

        Term ranker is acttive is use_categories is True

        """

        '''
        following Gries' notation, for the following example:
        b a m n i b e u p
        b a s a t b e w q n
        b c a g a b e s t a
        b a g h a b e a a t
        b a h a a b e a x a t

        (1) l = 50 (the length of the corpus in words)
        (2) n = 5 (the length of the corpus in parts)
        (3) s = (0.18, 0.2, 0.2, 0.2, 0.22) (the percentages of the n corpus part sizes)
        (4) f = 15 (the overall frequency of a in the corpus)
        (5) v = (1, 2, 3, 4, 5) (the frequencies of a in each corpus part 1-n)
        (6) p = (1/9, 2/10, 3/10, 4/10, 5 /11) (the percentages a makes up of each corpus part 1-n)
        
        Adapted from Burch: y is percentage of tokens which are a terms in a part   
        '''
        self.corpus = None
        self.use_metadata = non_text
        if corpus is None and term_doc_mat is None:
            raise Exception("Required non-None argument for corpus or term_doc_mat.")
        self.absent_vocab = []
        X = self.__get_X(corpus, non_text, term_doc_mat, term_ranker    , use_categories_as_documents)
        if corpus:
            if vocabulary is not None:
                self.absent_vocab = [v for v in vocabulary if v not in set(corpus.get_terms(use_metadata=non_text))]
            if self.absent_vocab:
                X = hstack([X, np.zeros((X.shape[0], len(self.absent_vocab)))])

        if add_smoothing_part:
            X = vstack([X, np.ones((1, X.shape[1]))])

        part_sizes = X.sum(axis=1)
        self.l = X.sum().sum()
        self.n = X.shape[0]
        self.f = X.sum(axis=0)
        self.term_part_counts = X  # v in Griess
        self.p_term_part = X.multiply(csc_matrix(1. / X.sum(axis=1)))
        self.prob_part = part_sizes / self.l  # s in gries
        self.tqdm = tqdm
        self.regressor = Lowess() if regressor is None else regressor

    def __get_X(self, corpus, non_text, term_doc_mat, term_ranker, use_categories):
        if term_doc_mat is not None:
            return term_doc_mat
        if corpus is not None:
            self.corpus = corpus
            if use_categories is True:
                if term_ranker is None:
                    term_ranker = AbsoluteFrequencyRanker

                term_ranker = term_ranker(term_doc_matrix=corpus).set_non_text(non_text=non_text)
                return csr_matrix(term_ranker.get_ranks('').values.T)
                # return term_ranker.get_ranks('').values
            else:
                X = corpus.get_term_doc_mat(non_text=non_text)
                return X
                # if non_text:
                # if use_categories is False:
                # X = corpus.get_metadata_doc_mat()
                # else:
                #    X = csr_matrix(corpus.get_metadata_freq_df().values.T)
                # else:
                # if use_categories is False:

                # else:
                # X = csr_matrix(corpus.get_term_freq_df().values.T)
        raise Exception()

    def dispersion_range(self):
        """
        range: number of parts containing a
        """
        return (self.term_part_counts > 0).sum(axis=0).A1

    def sd_population(self):
        return np.sqrt(StandardScaler(with_mean=False).fit(self.term_part_counts).var_)

    def vc(self):
        """
        Direct quote from Gries (2019)
        A maybe more useful variant of this measure is its normalized version, the variation
        coefficient (vc, see (9)); the normalization consists of dividing sdpopulation by the mean frequency
        of the element in the corpus parts f/n:
        """
        ss = StandardScaler(with_mean=False).fit(self.term_part_counts)
        return np.sqrt(ss.var_) / ss.mean_

    def jullands_d(self):
        """
        Direct quote from Gries (2019)

        The version of Juilland's D that can handle differently large corpus parts is then computed
        as shown in (10). In order to accommodate the different sizes of the corpus parts, however, the
        variation coefficient is not computed using the observed frequencies v1-n (i.e. 1, 2, 3, 4, 5 in files
        1 to 5 respectively, see (5) above) but using the percentages in p1-n (i.e. how much of each corpus
        part is made up by the element in question, i.e. 1/9, 2/10, 3/10, 4/10, 5/11, see (6) above), which is what
        corrects for differently large corpus parts:
        """
        ss = StandardScaler(with_mean=False).fit(self.p_term_part)
        return 1 - (np.sqrt(ss.var_) / ss.mean_) / np.sqrt(self.n - 1)

    def rosengrens(self):
        '''
        Direct quote from Gries (2019)

        The version of Rosengren’s S that can handle differently large corpus parts is
        shown in (12). Each corpus part size’s in percent (in s) is multiplied with the
        frequencies of the element in question in each corpus part (in v1-n); of each product,
        one takes the square root, and those are summed up, that sum is squared, and divided
        by the overall frequency of the element in question in the corpus (f)'''

        vs = self.term_part_counts.multiply(self.prob_part)
        return np.power(np.sqrt(vs).sum(axis=0).A1, 2) * 1. / self.get_frequency()

    def dp(self):
        '''
        Direct quote from Gries (2019)

        Finally, Gries (2008, 2010) and the follow-up by Lijffijt and Gries (2012)
        proposed a measure called DP (for deviation of proportions), which falls between
        1-min s (for an extremely even distribution) and 1 (for an extremely clumpy
        distribution) as well as a normalized version of DP, DPnorm, which falls between 0
        and 1, which are computed as shown in (13). For DP, one computes the differences
        between how much of the element in question is in each corpus file in percent on the
        one hand and the sizes of the corpus parts in percent on the other – i.e. the differences
        between observed and expected percentages. Then, one adds up the absolute values
        of those and multiplies by 0.5; the normalization then consists of dividing this values
        by the theoretically maximum value of DP given the number of corpus parts (in a
        way reminiscent of (11)'''
        return np.sum(np.abs(self.term_part_counts.multiply(1. / self.get_frequency()) - self.prob_part),
                      axis=0).A1 / 2

    def dp_norm(self):
        return self.dp() / (1 - self.prob_part.min())

    def kl_divergence(self):
        '''
        Direct quote from Gries (2019)
        The final measure to be discussed here is one that, as far as I can tell, has never
        been proposed as a measure of dispersion, but seems to me to be ideally suited to be
        one, namely the Kullback-Leibler (or KL-) divergence, a non-symmetric measure
        that quantifies how different one probability distribution (e.g., the distribution of
        all the occurrences of a across all corpus parts, i.e. v/f) is from another (e.g., the
        corpus part sizes s); the KL-divergence is computed as shown in (14) (with log2s of 167
        0 defined as 0):'''
        vf = self.term_part_counts.multiply(1. / self.f)
        vfs = vf.multiply(1. / self.prob_part)
        vfs.data = np.log(vfs.data) / np.log(2)
        return np.sum(vf.multiply(vfs), axis=0).A1

    def da(self):
        '''
        Metric from Burch (2017).

        Brent Burch, Jesse Egbertb and Douglas Biber. Measuring Lexical Dispersion in Corpus Linguistics. JRDS. 2016.
        Article: https://journal.equinoxpub.com/JRDS/article/view/9480

        D_A = 1 - ((n * (n - 1))/2) * sum_{i in 0, n - 1} sum{j in i + 1, n} |v_i - v_j|/(2*mean(v))

        :return:
        '''
        n = self.n

        constant = 1. / (n * (n - 1) / 2)

        ym = self.get_pct_of_term_in_part()

        it = range(self.term_part_counts.shape[1])
        if self.tqdm is not None:
            it = self.tqdm(it)

        da = []
        for word_i in it:
            y = ym.T[word_i]
            if type(y) != np.ndarray:
                y = y.todense().A1
            yt = np.tile(y, (n, 1))
            pairs_sum = np.sum(np.abs(yt - yt.T)) / 2
            da_score = 1 - pairs_sum * constant / (2 * y.mean())
            da.append(da_score)

        da_vec = np.array(da)
        da_vec[da_vec < 0] = 0  # correct for floating point issues
        return da_vec

    def get_pct_of_term_in_part(self) -> csr_matrix:
        # return burch's y
        # see https://stackoverflow.com/questions/49254111/row-division-in-scipy-sparse-matrix
        C = self.term_part_counts
        D = self.term_part_counts.sum(axis=1).A1
        r, c = C.nonzero()
        rD_sp = csr_matrix(((1.0 / D)[r], (r, c)), shape=(C.shape))
        return C.multiply(rD_sp)

    def get_df(self, terms=None, include_da=False, no_freq_metrics: Optional[List] = None):
        if terms is None and self.corpus is not None:
            terms = self.get_names()

        freq = self.get_frequency()
        df_content = {
            'Frequency': freq,
            'Range': self.dispersion_range(),
            'SD': self.sd_population(),
            'VC': self.vc(),
            "Juilland's D": self.jullands_d(),
            "Rosengren's S": self.rosengrens(),
            'DP': self.dp(),
            'DP norm': self.dp_norm(),
            'KL-divergence': self.kl_divergence(),
        }
        if include_da:
            df_content['DA'] = self.da()
        if terms is None:
            dispersion_df = pd.DataFrame(df_content)
        else:
            dispersion_df = pd.DataFrame(df_content, index=terms)

        if no_freq_metrics is not None:
            for metric in no_freq_metrics:
                dispersion_df = pd.merge(
                    dispersion_df,
                    dispersion_df.groupby('Frequency').apply(
                        lambda gdf: pd.Series({'Low': gdf[metric].min(), "Sup": gdf[metric].max()})
                    ),
                    left_on='Frequency',
                    right_index=True
                ).assign(**{
                    metric + '-nofreq': lambda df: ((df[metric] - df.Low) / (df.Sup - df.Low)).fillna(0.5)
                })
        return dispersion_df[lambda df: [c for c in df if c not in ['Low', 'Sups']]]

    def get_names(self):
        return self.corpus.get_terms(use_metadata=self.use_metadata) + self.absent_vocab

    def get_adjusted_metric(self, metric=None, freq=None):
        '''
        Returns the difference between DA and the Lowess estimate of DP from frequency

        :param metric: Optional[np.array], metric to analyze, defaults to DP

        :param freq: Optional[np.array], Word frequencies
        :return: np.array, frequency-adjusted metric
        '''
        if metric is None:
            observed = self.dp()
        elif metric == 'DA':
            observed = self.da()
        else:
            observed = self.get_df()[metric]

        if freq is None:
            freq = self.get_frequency()
        freq_est_metric = self.__fit_predict(freq, metric)
        return observed - freq_est_metric

    def get_adjusted_metric_df(
            self,
            metric: Optional[Union[str, np.array]] = None,
            freq: Optional[np.array] = None):
        '''
        Returns the difference between the metric and the Lowess estimate of metric from frequency

        :param metric: Optional[np.array], metric to analyze, defaults to DP

        :param freq: Optional[np.array], Word frequencies
        :return: np.array, frequency-adjusted metric
        '''
        if metric is None:
            metric = self.dp()
        elif metric == 'DA':
            metric = self.da()
        else:
            metric = self.get_df()[metric]

        if freq is None:
            freq = self.get_frequency()
        freq_est_metric = self.__fit_predict(freq, metric)
        adjusted_metric = metric - freq_est_metric
        return pd.DataFrame({
            'Frequency': freq,
            'Metric': metric,
            'Estimate': freq_est_metric,
            'Residual': adjusted_metric
        }, index=self.get_names())

    def __fit_predict(self, freq: np.array, metric: np.array, regressor: Optional[object] = None) -> np.array:
        if regressor is None:
            regressor = self.regressor
        fit_regressor = self.regressor.fit(freq.reshape(-1, 1), metric)
        pred = fit_regressor.predict(freq.reshape(-1, 1))
        freq_est_metric = pred.T[0]
        return freq_est_metric

    def get_frequency(self):
        if len(self.f.shape) == 1:
            return self.f
        return self.f.A1


def get_category_dispersion(
        corpus: TermDocMatrix,
        metric: str,
        corpus_to_parts: Optional[Callable[['TermDocMatrix'], List]] = None,
        include_residual: bool = False,
        include_residual_regressor: Optional[object] = None,
        non_text: bool = False
) -> pd.DataFrame:
    """

    :param corpus:  TermDocMatrix to process
    :param metric: a metric present in Dispersion.get_df. May be "DA".
    :param corpus_to_parts: Optional function which takes a TermDocMatrix and returns a list of parts of each doc. None indicates each doc is a separate part.
    :param non_text: Use non text features. False by default
    :param include_residual: Include the residual
    :param include_residual_regressor: Use a regressor for the residual computation
    :return: Dataframe giving category-specific features
    """
    data = {}
    for category in corpus.get_categories():
        category_corpus = corpus.remove_categories([c for c in corpus.get_categories() if c != category])
        if corpus_to_parts is not None:
            category_corpus = category_corpus.recategorize(corpus_to_parts)
        dispersion = Dispersion(
            category_corpus,
            non_text=non_text,
            use_categories_as_documents=corpus_to_parts is not None,
            vocabulary=corpus.get_terms(use_metadata=non_text), # this may be correct !!!
            add_smoothing_part=True
        )

        dispersion_df = dispersion.get_df(include_da=metric == 'DA')
        data[category + '_Frequency'] = dispersion_df.Frequency
        data[category + '_' + metric] = dispersion_df[metric]
        if include_residual:
            residual_df = dispersion.get_adjusted_metric_df(metric=metric)
            data[f'{category}_{metric}_Residual'] = residual_df['Residual']
            data[f'{category}_{metric}_Estimate'] = residual_df['Estimate']
    return pd.DataFrame(data)
