from collections import Counter
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc


class FeatsFromSentencePiece(FeatsFromSpacyDoc):
    def __init__(self, sp, *args, **kwargs):
        '''
        :param sp: sentencepiece.SentencePieceProcessor
        '''
        self._sp = sp
        super(FeatsFromSentencePiece, self).__init__(*args, **kwargs)

    def get_doc_metadata(self, doc):
        '''

        :param doc: spacy.Doc
        :return: pd.Series
        '''
        return Counter(self._sp.encode_as_pieces(str(doc)))