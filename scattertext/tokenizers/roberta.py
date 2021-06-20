from scattertext.WhitespaceNLP import Tok, _get_pos_tag, Doc


class RobertaTokenizerWrapper:
    '''
    Encapsulates the roberta tokenizer
    '''
    def __init__(self,
                 tokenizer,
                 decoder=None,
                 entity_type=None,
                 tag_type=None):
        self.tokenizer = tokenizer
        if decoder is None:
            try:
                from text_unidecode import unidecode
            except:
                raise Exception("Please install the text_unicode package to preprocess documents. "
                                "If you'd like to bypass this step, pass a text preprocessing "
                                "(e.g., lambda x: x) function into the decode parameter of this class.")
            self.decoder = unidecode
        else:
            self.decoder = decoder
        self.entity_type = entity_type
        self.tag_type = tag_type

    def tokenize(self, doc):
        '''
        doc: str, text to be tokenized
        '''

        sents = []
        decoded_text = self.decoder(doc)
        tokens = self.tokenizer.convert_ids_to_tokens(
            self.tokenizer(decoded_text)['input_ids'],
            skip_special_tokens=True
        )

        last_idx = 0
        toks = []
        for raw_token in tokens:
            token_surface_string = raw_token
            if ord(raw_token[0]) == 288:
                token_surface_string = raw_token[1:]
            if ord(raw_token[0]) == 266: # skip new lines
                last_idx += len(raw_token)
                continue
            token_idx = decoded_text.index(token_surface_string, last_idx)
            toks.append(Tok(_get_pos_tag(token_surface_string),
                            token_surface_string.lower(),
                            raw_token.lower(),
                            ent_type='' if self.entity_type is None else self.entity_type.get(token_surface_string, ''),
                            tag='' if self.tag_type is None else self.tag_type.get(token_surface_string, ''),
                            idx=token_idx))
            last_idx = token_idx + len(token_surface_string)
            if token_surface_string in ['.', '!', '?']: # idiot's sentence splitter
                sents.append(toks)
                toks = []

        if len(toks) > 0:
            sents.append(toks)
        return Doc(sents, decoded_text)


    def get_subword_encoding_name(self):
        return 'RoBERTa'