import pandas as pd
import scipy
from pandas import DataFrame
from scipy.sparse import issparse
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler, StandardScaler

from scattertext.representations.Doc2VecBuilder import Doc2VecBuilder
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.categoryprojector.CategoryProjection import CategoryProjection, CategoryProjectionWithDoc2Vec
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor
from sklearn.decomposition import PCA

'''
class LengthNormalizeScaleStandardize(object):
    def fit_transform(self, X):
        compact_category_counts_catscale = X / X.sum(axis=0)
        compact_category_counts_catscale_std = (
                compact_category_counts_catscale.T - compact_category_counts_catscale.mean(axis=1)).T
        compact_category_counts_catscale_std_scale = (
                compact_category_counts_catscale_std.T / compact_category_counts_catscale_std.std(axis=1)).T
        return compact_category_counts_catscale_std_scale
'''

class LengthNormalizer(BaseEstimator, TransformerMixin):
    def fit_transform(self, X, y=None, **fit_params):
        return X - X.sum(axis=0)


class LengthNormalizeRobustScale(object):
    def fit_transform(self, X):
        compact_category_counts_catscale = X / X.sum(axis=0)
        compact_category_counts_catscale_std = (
                compact_category_counts_catscale.T - compact_category_counts_catscale.mean(axis=1)).T
        return RobustScaler().fit_transform(compact_category_counts_catscale_std)


class CategoryProjectorBase(object):
    def project(self, term_doc_mat, x_dim=0, y_dim=1):
        '''
        Returns a projection of the categories

        :param term_doc_mat: a TermDocMatrix
        :return: CategoryProjection
        '''
        return self._project_category_corpus(
            self._get_category_metadata_corpus(term_doc_mat),
            x_dim,
            y_dim
        )

    def project_with_metadata(self, term_doc_mat, x_dim=0, y_dim=1):
        '''
        Returns a projection of the

        :param term_doc_mat: a TermDocMatrix
        :return: CategoryProjection
        '''
        return self._project_category_corpus(
            self._get_category_metadata_corpus_and_replace_terms(term_doc_mat),
            x_dim,
            y_dim
        )

    def _project_category_corpus(self, category_corpus, x_dim=0, y_dim=1):
        raise NotImplementedError()

    def _get_category_metadata_corpus(self, corpus):
        raise NotImplementedError()

    def _get_category_metadata_corpus_and_replace_terms(self, corpus):
        raise NotImplementedError()

    def get_category_embeddings(self, corpus):
        '''
        :param corpus: TermDocMatrix

        :return: np.array, matrix of (num categories, embedding dimension) dimensions
        '''
        raise NotImplementedError()


class CategoryProjector(CategoryProjectorBase):
    def __init__(self,
                 weighter=LengthNormalizer(),
                 normalizer=StandardScaler(),
                 selector=AssociationCompactor(1000, RankDifference),
                 projector=PCA(2)):
        '''

        :param weighter: instance of an sklearn class with fit_transform to weight X category corpus.
        :param normalizer: instance of an sklearn class with fit_transform to normalize term X category corpus.
        :param selector: instance of a compactor class, if None, no compaction will be done.
        :param projector: instance an sklearn class with fit_transform
        '''
        self.weighter_ = weighter
        self.normalizer_ = normalizer
        self.selector_ = selector
        self.projector_ = projector

    def get_category_embeddings(self, category_corpus):
        raw_category_counts = self._get_raw_category_counts(category_corpus)
        weighted_counts = self.weight(raw_category_counts)
        normalized_counts = self.normalize(weighted_counts)
        if type(normalized_counts) is not pd.DataFrame:
            normalized_counts = pd.DataFrame(normalized_counts.todense()
                                             if scipy.sparse.issparse(normalized_counts)
                                             else normalized_counts,
                                             columns=raw_category_counts.columns,
                                             index=raw_category_counts.index)
        return normalized_counts

    def _get_raw_category_counts(self, category_corpus):
        return category_corpus.get_term_freq_df('')

    def weight(self, category_counts):
        if self.weighter_ is None:
            return category_counts
        return self.weighter_.fit_transform(category_counts)

    def normalize(self, weighted_category_counts):
        if self.normalizer_ is not None:
            normalized_vals = self.normalizer_.fit_transform(weighted_category_counts)
            if issparse(normalized_vals):
                return normalized_vals
            if not isinstance(normalized_vals, DataFrame):
                return DataFrame(data=normalized_vals,
                                 columns=weighted_category_counts.columns,
                                 index=weighted_category_counts.index)
            else:
                return normalized_vals
        return weighted_category_counts

    def select(self, corpus):
        if self.selector_ is not None:
            corpus = corpus.select(self.selector_)
        return corpus

    def _project_category_corpus(self, category_corpus, x_dim=0, y_dim=1):
        normalized_counts = self.get_category_embeddings(category_corpus)
        proj = self.projector_.fit_transform(normalized_counts.T)
        return CategoryProjection(category_corpus, normalized_counts, proj, x_dim=x_dim, y_dim=y_dim)

    def _get_category_metadata_corpus(self, corpus):
        return self.select(corpus).use_categories_as_metadata()

    def _get_category_metadata_corpus_and_replace_terms(self, corpus):
        return self.select(corpus).use_categories_as_metadata_and_replace_terms()




class Doc2VecCategoryProjector(CategoryProjectorBase):
    def __init__(self, doc2vec_builder=None, projector=PCA(2)):
        '''

        :param doc2vec_builder: Doc2VecBuilder, optional
            If None, a default model will be used
        :param projector: object
            Has fit_transform method
        '''
        if doc2vec_builder is None:
            try:
                import gensim
            except:
                raise Exception("Please install gensim before using Doc2VecCategoryProjector/")
            self.doc2vec_builder = Doc2VecBuilder(
                gensim.models.Doc2Vec(vector_size=100, window=5, min_count=5, workers=6, alpha=0.025,
                                      min_alpha=0.025, epochs=50)
            )
        else:
            assert type(doc2vec_builder) == Doc2VecBuilder
            self.doc2vec_builder = doc2vec_builder
        self.projector = projector

    def _project_category_corpus(self, corpus, x_dim=0, y_dim=1):
        try:
            import gensim
        except:
            raise Exception("Please install gensim before using Doc2VecCategoryProjector/")

        category_corpus = corpus.use_categories_as_metadata()
        category_counts = corpus.get_term_freq_df('')
        self.doc2vec_builder.train(corpus)

        proj = self.projector.fit_transform(self.doc2vec_builder.project())
        return CategoryProjectionWithDoc2Vec(category_corpus,
                                             category_counts,
                                             proj,
                                             x_dim=x_dim,
                                             y_dim=y_dim,
                                             doc2vec_model=self.doc2vec_builder)

    def _get_category_metadata_corpus(self, corpus):
        return corpus.use_categories_as_metadata()

    def _get_category_metadata_corpus_and_replace_terms(self, corpus):
        return corpus.use_categories_as_metadata_and_replace_terms()

    def get_category_embeddings(self, corpus):
        return self.doc2vec_builder.project()


