from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_frequency_explorer, HedgesR
from scattertext.CorpusFromPandas import CorpusFromPandas

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = (CorpusFromPandas(convention_df,
                           category_col='party',
                           text_col='text',
                           nlp=whitespace_nlp_with_sentences)
          .build()
          .get_unigram_corpus())

html = produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    term_scorer=HedgesR(corpus),
    metadata=convention_df['speaker'],
    grey_threshold=0
)

file_name = 'demo_hedges_r.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
