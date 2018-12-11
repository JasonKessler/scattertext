import re

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import pearsonr

from scattertext.representations import Word2VecFromParsedCorpus


class EmbeddingsResolver:
    def __init__(self, corpus):
        self.corpus_ = corpus
        self.embeddings_ = None
        self.word2vec_model_ = None

    def set_embeddings(self, embeddings):
        '''
        Specifies fixed set of embeddings
        :param embeddings: array-like, sparse or dense, shape should be (embedding size, # terms)
        :return: EmbeddingsResolver
        '''
        if self.embeddings_ is not None:
            raise Exception("You have already set embeddings by running set_embeddings or set_embeddings_model.")
        assert embeddings.shape[1] == self.corpus_.get_num_terms()
        self.embeddings_ = embeddings.T
        self.vocab_ = self.corpus_.get_terms()
        return self

    def set_embeddings_model(self, model=None, term_acceptance_re=re.compile('[a-z]{3,}')):
        '''

        :param model: gensim word2vec.Word2Vec model
        :param term_acceptance_re : SRE_Pattern, Regular expression to identify
            valid terms, default re.compile('[a-z]{3,}')
        :return: EmbeddingsResolver
        '''
        if self.embeddings_ is not None:
            raise Exception("You have already set embeddings by running set_embeddings or set_embeddings_model.")
        self.word2vec_model_ = model
        if term_acceptance_re is not None:
            acceptable_terms = set([t for t in self.corpus_.get_terms() if term_acceptance_re.match(t)])
        else:
            acceptable_terms = set(self.corpus_.get_terms())
        model = Word2VecFromParsedCorpus(self.corpus_, model).train()
        self.corpus_ = self.corpus_.remove_terms(set(self.corpus_.get_terms()) - acceptable_terms)
        weight_list = [model[word] for word in model.wv.vocab]
        self.embeddings_ = np.stack(weight_list)
        self.vocab_ = model.wv.vocab
        return self


    def project_embeddings(self, projection_model=None, x_dim=0, y_dim=1):
        '''

        :param projection_model: sklearn unsupervised model (e.g., PCA) by default the recommended model is umap.UMAP,
            which requires UMAP in to be installed
        :param x_dim: int, default 0, dimension of transformation matrix for x-axis
        :param y_dim: int, default 1, dimension of transformation matrix for y-axis
        :return:
        '''
        axes = self.project(projection_model)
        word_axes = (pd.DataFrame({'term': [w for w in self.vocab_],
                                   'x': axes.T[x_dim],
                                   'y': axes.T[y_dim]})
                     .set_index('term')
                     .reindex(pd.Series(self.corpus_.get_terms()))
                     .dropna())
        self.corpus_ = self.corpus_.remove_terms(set(self.corpus_.get_terms()) - set(word_axes.index))
        word_axes = word_axes.reindex(self.corpus_.get_terms()).dropna()

        return self.corpus_, word_axes

    '''
    def get_svd(self, num_dims, category):
        U, s, V = sparse.linalg.svds(self.corpus_._X.astype('d'), k=num_dims)
        Y = self.corpus_.get_category_ids() == category
        [pearsonr(U.T[i], ) for i in range(num_dims)]
    '''

    def project(self, projection_model=None):
        '''
        :param projection_model: sklearn unsupervised model (e.g., PCA) by default the recommended model is umap.UMAP,
        which requires UMAP in to be installed

        :return: array, shape (num dimension, vocab size)
        '''
        if self.embeddings_ is None:
            raise Exception("Run set_embeddings_model or set_embeddings to get embeddings")
        if projection_model is None:
            try:
                import umap
            except:
                raise Exception("Please install umap (pip install umap-learn) to use the default projection_model.")
            projection_model = umap.UMAP(min_dist=0.5, metric='cosine')
        axes = projection_model.fit_transform(self.embeddings_)
        return axes
