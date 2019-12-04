import scattertext as st
import tempfile
import sentencepiece as spm

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df.text.apply(st.whitespace_nlp_with_sentences)

def train_sentence_piece_tokenizer(documents, vocab_size):
    '''
    :param documents: list-like, a list of str documents
    :vocab_size int: the size of the vocabulary to output

    :return sentencepiece.SentencePieceProcessor
    '''
    sp = None
    with tempfile.NamedTemporaryFile(delete=True) as tempf:
        with tempfile.NamedTemporaryFile(delete=True) as tempm:
            tempf.write(('\n'.join(documents)).encode())
            mod = spm.SentencePieceTrainer.Train('--input=%s --model_prefix=%s --vocab_size=%s'
                                                 % (tempf.name, tempm.name, vocab_size))
            sp = spm.SentencePieceProcessor()
            sp.load(tempm.name + '.model')
    return sp

sp = train_sentence_piece_tokenizer(convention_df.text.values, 2000)

corpus = st.CorpusFromParsedDocuments(
    convention_df,
    parsed_col='parse',
    category_col='party',
    feats_from_spacy_doc=st.FeatsFromSentencePiece(sp)
).build()

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    sort_by_dist=False,
    metadata=convention_df['party'] + ': ' + convention_df['speaker'],
    term_scorer=st.RankDifference(),
    transform=st.Scalers.dense_rank,
    use_non_text_features=True,
    use_full_doc=True,
)
file_name = 'demo_sentence_piece.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
