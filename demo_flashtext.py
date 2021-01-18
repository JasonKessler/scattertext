from collections import Counter
from flashtext import KeywordProcessor
import scattertext as st


class FlashTextExtact(st.FeatsFromSpacyDoc):
    '''

    '''
    def set_keyword_processor(self, keyword_processor):
        '''
    
        :param keyword_processor: set, phrases to look for
        :return: self
        '''
        self.keyword_processor_ = keyword_processor
        return self

    def get_feats(self, doc):
        '''
        Parameters
        ----------
        doc, Spacy Doc

        Returns
        -------
        Counter noun chunk -> count
        '''
        return Counter(self.keyword_processor_.extract_keywords(str(doc)))


keyword_processor = KeywordProcessor(case_sensitive=False)
for phrase in ['the president', 'presidents', 'presidential', 'barack obama', 'mitt romney', 'george bush',
               'george w. bush', 'bill clinton', 'ronald regan', 'obama', 'romney',
               'barack', 'mitt', 'bush', 'clinton', 'reagan', 'mr. president', 'united states of america']:
        keyword_processor.add_keyword(phrase)
feature_extractor = FlashTextExtact().set_keyword_processor(keyword_processor)

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df['text'].apply(st.whitespace_nlp_with_sentences)
corpus = (st.CorpusFromPandas(convention_df,
                              category_col='party',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences,
                              feats_from_spacy_doc=feature_extractor)
          .build())

print(corpus.get_term_freq_df())

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    metadata=convention_df['speaker'],
    term_scorer=st.RankDifference(),
    transform=st.Scalers.dense_rank,
    pmi_threshold_coefficient=0,
    minimum_term_frequency=0,
    minimum_not_category_term_frequency=0,
    use_full_doc=True
)

file_name = 'demo_specific_phrases.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)
