from pandas import DataFrame
from sklearn.preprocessing import RobustScaler

from scattertext.termscoring.RankDifference import RankDifference
from scattertext.cartegoryprojector.CategoryProjection import CategoryProjection
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor
from sklearn.decomposition import PCA


class LengthNormalizeScaleStandardize(object):
    def fit_transform(self, X):
        compact_category_counts_catscale = X / X.sum(axis=0)
        compact_category_counts_catscale_std = (
                compact_category_counts_catscale.T - compact_category_counts_catscale.mean(axis=1)).T
        compact_category_counts_catscale_std_scale = (
                compact_category_counts_catscale_std.T / compact_category_counts_catscale_std.std(axis=1)).T
        return compact_category_counts_catscale_std_scale


class LengthNormalizeRobustScale(object):
    def fit_transform(self, X):
        compact_category_counts_catscale = X / X.sum(axis=0)
        compact_category_counts_catscale_std = (
                compact_category_counts_catscale.T - compact_category_counts_catscale.mean(axis=1)).T
        return RobustScaler().fit_transform(compact_category_counts_catscale_std)


class CategoryProjector(object):
    def __init__(self,
                 compactor=AssociationCompactor(1000, RankDifference),
                 normalizer=LengthNormalizeScaleStandardize(),
                 projector=PCA(2)):
        '''

        :param compactor: instance of a compactor class, if None, no compaction will be done.
        :param projector: instance an sklearn class with fit_transform
        :param normalizer: instance of an sklearn class with fit_transform to normalize term X category corpus.
        '''
        self.compactor_ = compactor
        self.projector_ = projector
        self.normalizer_ = normalizer

    def project(self, term_doc_mat, x_dim=0, y_dim=1):
        '''
        Returns a projection of the

        :param term_doc_mat: a TermDocMatrix
        :return: pd.DataFrame, TermDocMatrix
        '''
        return self._project_category_corpus(self._get_category_metadata_corpus(term_doc_mat), x_dim, y_dim)

    def project_with_metadata(self, term_doc_mat, x_dim=0, y_dim=1):
        '''
        Returns a projection of the

        :param term_doc_mat: a TermDocMatrix
        :return: pd.DataFrame, TermDocMatrix
        '''
        return self._project_category_corpus(self._get_category_metadata_corpus_and_replace_terms(term_doc_mat), x_dim,
                                             y_dim)

    def _project_category_corpus(self, category_corpus, x_dim=0, y_dim=1):
        category_counts = self.normalize(category_corpus.get_term_freq_df(''))
        proj = self.projector_.fit_transform(category_counts.T)
        return CategoryProjection(category_corpus, category_counts, proj, x_dim=x_dim, y_dim=y_dim)

    def normalize(self, category_counts):
        if self.normalizer_ is not None:
            normalized_vals = self.normalizer_.fit_transform(category_counts)
            if not isinstance(normalized_vals, DataFrame):
                return DataFrame(data=normalized_vals, columns=category_counts.columns, index=category_counts.index)
            else:
                return normalized_vals
        return category_counts

    def _get_category_metadata_corpus(self, corpus):
        return self.compact(corpus).use_categories_as_metadata()

    def _get_category_metadata_corpus_and_replace_terms(self, corpus):
        return self.compact(corpus).use_categories_as_metadata_and_replace_terms()

    def compact(self, corpus):
        if self.compactor_ is not None:
            corpus = corpus.compact(self.compactor_)
        return corpus
