import pandas as pd
from unittest import TestCase

import numpy as np
from sklearn.decomposition import TruncatedSVD

from scattertext import EmbeddingsResolver, ClassPercentageCompactor, CorpusFromPandas, whitespace_nlp, \
    CorpusFromParsedDocuments, ParsedCorpus
from scattertext.test.test_CorpusFromParsedDocuments import build_term_doc_matrix
from scattertext.test.test_corpusFromPandas import get_docs_categories


class WV:
    def __init__(self, vocab):
        self.vocab = vocab


class MockWord2Vec:
    def __init__(self, vocab):
        self.wv = WV(vocab)
        self.corpus_count = 5

    def train(self, *args, **kwargs):
        pass

    def build_vocab(self, *args):
        pass

    def __getitem__(self, item):
        assert item in self.wv.vocab
        return np.zeros(30)



class TestEmbeddingsResolver(TestCase):
    @classmethod
    def setUp(cls):
        categories, documents = get_docs_categories()
        cls.df = pd.DataFrame({'category': categories,
                               'text': documents})
        cls.df['parsed'] = cls.df.text.apply(whitespace_nlp)
        cls.corpus = CorpusFromParsedDocuments(cls.df, 'category', 'parsed').build()

    def test_resolve_embeddings(self):
        tdm = self.corpus.get_unigram_corpus().select(ClassPercentageCompactor(term_count=1))
        embeddings_resolver = EmbeddingsResolver(tdm)
        # embeddings = TruncatedSVD(n_components=20).fit_transform(tdm.get_term_doc_mat().T).T
        # embeddings_resolver.set_embeddings(embeddings)
        embeddings_resolver = embeddings_resolver.set_embeddings(tdm.get_term_doc_mat())
        if self.assertRaisesRegex:
            with self.assertRaisesRegex(Exception,
                                        "You have already set embeddings by running set_embeddings or set_embeddings_model."):
                embeddings_resolver.set_embeddings_model(None)
        embeddings_resolver = EmbeddingsResolver(tdm)

        embeddings_resolver = embeddings_resolver.set_embeddings_model(MockWord2Vec(tdm.get_terms()))
        if self.assertRaisesRegex:
            with self.assertRaisesRegex(Exception,
                                        "You have already set embeddings by running set_embeddings or set_embeddings_model."):
                embeddings_resolver.set_embeddings(tdm.get_term_doc_mat())
        c, axes = embeddings_resolver.project_embeddings(projection_model=TruncatedSVD(3))
        self.assertIsInstance(c, ParsedCorpus)
        self.assertEqual(axes.to_dict(), pd.DataFrame(index=['speak'], data={'x': [0.,], 'y':[0.,]}).to_dict())
