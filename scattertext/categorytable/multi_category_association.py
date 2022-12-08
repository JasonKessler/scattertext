class MultiCategoryAssociationBase:
    def __init__(self, corpus, use_metadata=False):
        self.corpus = corpus
        self.use_metadata = use_metadata

    def get_category_association(self):
        raise NotImplementedError()
