class CoefficientBase:
    def __init__(self, use_non_text=False):
        self.use_non_text = use_non_text

    def _get_tdm(self, corpus):
        return corpus.get_metadata_doc_mat() if self.use_non_text else corpus.get_term_doc_mat()

    def _get_terms(self, corpus):
        return corpus.get_metadata() if self.use_non_text else corpus.get_terms()