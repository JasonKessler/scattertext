from scattertext.termscoring.RankDifference import RankDifference
from scattertext.cartegoryprojector.CategoryProjection import CategoryProjection
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor
from sklearn.decomposition import PCA


class CategoryProjector(object):
    def __init__(self,
                 compactor=AssociationCompactor(1000, RankDifference),
                 projector=PCA(2)):
        '''

        :param compactor: instance of a compactor class
        :param projector: instance a sklearn class with fit_transform
        '''
        self.compactor_ = compactor
        self.projector_ = projector

    def project(self, term_doc_mat):
        '''
        Returns a projection of the

        :param term_doc_mat: a TermDocMat
        :return: pd.DataFrame, TermDocMat
        '''
        category_corpus = self._get_category_metadata_corpus(term_doc_mat)
        category_counts = self._scale_and_standardize(category_corpus.get_term_freq_df('').astype('f'))
        proj = self.projector_.fit_transform(category_counts.T)
        return CategoryProjection(category_corpus, category_counts, proj)

    def _scale_and_standardize(self, category_counts):
        compact_category_counts_catscale = category_counts / category_counts.sum(axis=0)
        compact_category_counts_catscale_std = (
                compact_category_counts_catscale.T - compact_category_counts_catscale.mean(axis=1)).T
        compact_category_counts_catscale_std_scale = (
                compact_category_counts_catscale_std.T / compact_category_counts_catscale_std.var(axis=1)).T
        return compact_category_counts_catscale_std_scale

    def _get_category_metadata_corpus(self, corpus):
        if self.compactor_ is not None:
            corpus = corpus.compact(self.compactor_)
        return corpus.use_categories_as_metadata()
