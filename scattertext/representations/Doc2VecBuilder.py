import itertools

from scattertext.ParsedCorpus import ParsedCorpus


class Doc2VecBuilder(object):
    def __init__(self, model, term_from_token=lambda tok: tok.lower_):
        self.model = model
        self.term_from_token = term_from_token
        self.cartegory2dvid = None
        self.corpus = None

    def train(self, corpus):
        assert isinstance(corpus, ParsedCorpus)
        tagged_docs = []
        try:
            import gensim
        except:
            raise Exception("Please install gensim before using Doc2VecCategoryProjector/")
        for doc, tag in zip(corpus.get_parsed_docs(), corpus.get_category_names_by_row()):
            words = list(itertools.chain(
                *[[t.lower_ for t in sent if not t.is_punct if t.lower_.strip()] for sent in doc.sents]))
            tagged_docs.append(gensim.models.doc2vec.TaggedDocument(words, [tag]))

        self.model.build_vocab(tagged_docs)

        self.cartegory2dvid = {}
        for i in range(corpus.get_num_categories()):
            self.cartegory2dvid[self.model.docvecs.index_to_doctag(i)] = i

        self.model.train(tagged_docs, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        self.corpus = corpus
        return self.model

    def project(self):
        if self.corpus is None:
            raise Exception("Please run train before project.")
        return self.model.docvecs.vectors_docs[
            [self.cartegory2dvid[category] for category in self.corpus.get_categories()]]