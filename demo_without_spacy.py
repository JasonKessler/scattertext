
from scattertext import SampleCorpora
from scattertext import produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.WhitespaceNLP import whitespace_nlp

nlp = whitespace_nlp

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=nlp).build()

html = produce_scattertext_explorer(corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    minimum_term_frequency=5,
                                    pmi_filter_thresold=4,
                                    width_in_pixels=1000,
                                    metadata=convention_df['speaker'])
open('./demo_without_spacy.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_without_spacy.html in Chrome or Firefox.')
