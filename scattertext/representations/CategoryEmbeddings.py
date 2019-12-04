import itertools
import re
import warnings

import numpy as np
import pandas as pd
import scipy
from sklearn.metrics.pairwise import cosine_similarity
from scattertext import ParsedCorpus
from scattertext.representations.Word2VecFromParsedCorpus import Word2VecDefault


class CategoryEmbeddingsResolver:
    def __init__(self, corpus, term_acceptance_re=re.compile('[a-z]{3,}')):
        self.corpus_ = corpus
        self.category_embeddings_ = {}
        self.category_word2vec_model_ = {}
        self.term_acceptance_re = term_acceptance_re

    def _verify_category(self, category):
        if category not in self.corpus_.get_categories():
            raise Exception("Category %s is not in corpus." % category)
        if category in self.category_embeddings_:
            raise Exception("You have already set embeddings by running set_embeddings or set_embeddings_model.")

    def embed_category(self, category, model=None):
        '''

        :param model: gensim word2vec.Word2Vec model
        :param term_acceptance_re : SRE_Pattern, Regular expression to identify
            valid terms, default re.compile('[a-z]{3,}')
        :return: EmbeddingsResolver
        '''
        self._verify_category(category)
        if self.term_acceptance_re is not None:
            acceptable_terms = set([t for t in self.corpus_.get_terms() if self.term_acceptance_re.match(t)])
        else:
            acceptable_terms = set(self.corpus_.get_terms())
        trained_model = CategorySpecificWord2VecFromParsedCorpus(self.corpus_, category, model).train()
        self.category_word2vec_model_[category] = trained_model
        word2dwe = {word: trained_model[word] for word in trained_model.wv.vocab.keys()}
        self.category_embeddings_[category] = word2dwe
        return self

    def embed_all_categories(self):
        for category in self.corpus_.get_categories():
            self.embed_category(category)
        return self



class CartegorySpecificCorpusAdapterForGensim(object):
    @staticmethod
    def get_sentences(corpus, category):
        '''
        Parameters
        ----------
        corpus, ParsedCorpus
        category, str

        Returns
        -------
        iter: [sentence1word1, ...], [sentence2word1, ...]
        '''
        #assert isinstance(corpus, ParsedCorpus)
        return itertools.chain(*[[[t.lower_ for t in sent if not t.is_punct]
                                  for sent in doc.sents]
                                 for doc_catgory, doc
                                 in zip(corpus.get_category_names_by_row(), corpus.get_parsed_docs())
                                 if category == doc_catgory])




class CategorySpecificWord2VecFromParsedCorpus(Word2VecDefault):
    def __init__(self, corpus, category, word2vec_model=None):
        '''
        Parameters
        ----------
        corpus: ParsedCorpus
          from which to build word2vec model
        category, str
        word2vec_model: word2vec.Word2Vec
            Gensim instance to be used to train word2vec model
        '''
        try:
            from gensim.models import word2vec
            assert word2vec_model is None or isinstance(word2vec_model, word2vec.Word2Vec)
        except:
            warnings.warn("You should really install gensim, but we're going to duck-type your model and hope it works")
        #print(type(corpus))
        #assert isinstance(corpus, ParsedCorpus)
        self.corpus = corpus
        self.category = category
        self.model = self._get_word2vec_model(word2vec_model)

    def train(self, epochs=2000, training_iterations=5):
        '''
        Parameters
        ----------
        epochs : int
          Number of epochs to train for.  Default is 2000.
        training_iterations : int
            Number of times to repeat training process. Default is training_iterations.

        Returns
        -------
        A trained word2vec model.
        '''

        self._scan_and_build_vocab()
        for _ in range(training_iterations):
            self.model.train(CartegorySpecificCorpusAdapterForGensim.get_sentences(self.corpus, self.category),
                             total_examples=self.model.corpus_count,
                             epochs=epochs)
        return self.model

    def _get_word2vec_model(self, word2vec_model):
        return (self._default_word2vec_model()
                if word2vec_model is None
                else word2vec_model)

    def _scan_and_build_vocab(self):
        try:
            self.model.scan_vocab(CartegorySpecificCorpusAdapterForGensim.get_sentences(self.corpus, self.category))
        except:
            pass
        self.model.build_vocab(CartegorySpecificCorpusAdapterForGensim.get_sentences(self.corpus, self.category))


class EmbeddingAligner(object):
    def __init__(self, category_embedding_resolver, category1, category2, prefix1=None, prefix2=None):
        '''

        :param category_embedding_resolver: CategoryEmbeddingsResolver
        :param category1: str
        :param category2: str
        :param prefix1: str
        :param prefix2: str
        '''
        #assert issubclass(type(category_embedding_resolver), CategoryEmbeddingsResolver)
        self.category_embedding_resolver = category_embedding_resolver
        valid_categories = category_embedding_resolver.corpus_.get_categories()
        assert category1 in valid_categories
        assert category2 in valid_categories
        self.category1 = category1
        self.category2 = category2
        cat1_dwe_dict = category_embedding_resolver.category_embeddings_[category1]
        cat2_dwe_dict = category_embedding_resolver.category_embeddings_[category2]
        self.terms = np.array(list((set(cat1_dwe_dict.keys()) & set(cat2_dwe_dict.keys()))))
        self.cat1_dwe_ar = np.stack([cat1_dwe_dict[word] for word in self.terms])
        self.cat2_dwe_ar = np.stack([cat2_dwe_dict[word] for word in self.terms])

        #self.cat1_dwe_ar_norm, self.cat2_dwe_ar_norm, self.disparity = \
        #    scipy.spatial.procrustes(self.cat1_dwe_ar, self.cat2_dwe_ar)
        self.pairwise_sim, sv = scipy.linalg.orthogonal_procrustes(self.cat1_dwe_ar, self.cat2_dwe_ar)

        import pdb; pdb.set_trace()

        #self.pairwise_sim = cosine_similarity(np.vstack([self.cat1_dwe_ar_norm,
        #                                                 self.cat2_dwe_ar_norm]))
        #

        self.pairwise_sim_sort = np.argsort(-self.pairwise_sim, axis=1)

        def distinct_prefix(x, y):
            for i, (xc, yc) in enumerate(zip(x, y)):
                if xc != yc:
                    return (x[:i + 1], y[:i + 1])
            return x, y

        myprefix1, myprefix2 = distinct_prefix(category1, category2)
        self.prefix1 = myprefix1 if prefix1 is None else prefix1
        self.prefix2 = myprefix2 if prefix2 is None else prefix2

        self.labeled_terms = np.array([self.prefix1 + '_' + w for w in self.terms]
                                      + [self.prefix2 + '_' + w for w in self.terms])

    def get_terms(self):
        return self.terms

    def project_separate(self, projector=None):
        if projector is None:
            from umap import UMAP
            projector = UMAP(n_components=2, metric='cosine')
        both_category_embeddings = np.vstack([self.cat1_dwe_ar_norm,
                                              self.cat2_dwe_ar_norm])
        projected_ar = projector.fit_transform(both_category_embeddings)
        df = pd.DataFrame(projected_ar, columns=['x', 'y'], index=self.labeled_terms)
        df['category'] = [self.category1] * len(self.terms) + [self.category2] * len(self.terms)
        return df

    def get_report_df(self, n_terms=5):
        conterpart_idx = np.hstack([np.arange(len(self.terms)) + len(self.terms),
                                    np.arange(len(self.terms))])
        idx = np.arange(len(self.terms))
        similarity_df = pd.DataFrame({
            'cosine_distance': self.pairwise_sim[[idx], conterpart_idx[idx]][0],
            'rank_' + self.prefix1: np.where(
                self.pairwise_sim_sort[idx] == conterpart_idx[idx][:, None]
            )[1],
            'rank_' + self.prefix2: np.where(
                self.pairwise_sim_sort[conterpart_idx[idx]] == idx[:, None]
            )[1],
            'context_' + self.prefix1: pd.DataFrame(
                self.labeled_terms[self.pairwise_sim_sort[idx, 1:1 + n_terms]]
            ).apply(', '.join, axis=1).values,
            'context_' + self.prefix2: pd.DataFrame(
                self.labeled_terms[self.pairwise_sim_sort[conterpart_idx[idx], 1:1 + n_terms]]
            ).apply(', '.join, axis=1).values,
        },
            index=self.terms
        )
        return pd.merge(
            similarity_df
                .assign(min_rank=lambda x: np.max(x[['rank_' + self.prefix1, 'rank_' + self.prefix1]], axis=1))
                .sort_values(by='min_rank', ascending=False),
            self.category_embedding_resolver.corpus_
                .get_term_freq_df(),
            left_index=True,
            right_index=True
        )


