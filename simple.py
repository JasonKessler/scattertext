import spacy

from scattertext import SampleCorpora
from scattertext import produce_scattertext_explorer, produce_scattertext_html
from scattertext.CorpusFromPandas import CorpusFromPandas

nlp = spacy.en.English()
convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=nlp).build()

html = produce_scattertext_html(corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    minimum_term_frequency=5,
                                    pmi_filter_thresold=4,
                                    width_in_pixels=1000)
open('./simple.html', 'wb').write(html.encode('utf-8'))
print('Open ./simple.html in Chrome or Firefox.')
