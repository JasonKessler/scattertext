from scattertext import SampleCorpora, whitespace_nlp_with_sentences, CohensD, produce_frequency_explorer, \
    OncePerDocFrequencyRanker
from scattertext.termcompaction.ClassPercentageCompactor import ClassPercentageCompactor
from scattertext import produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.termscoring.ScaledFScore import ScaledFScorePresets

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = (CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=whitespace_nlp_with_sentences)
          .build()
          .compact(ClassPercentageCompactor(term_ranker=OncePerDocFrequencyRanker)))

html = produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    term_scorer=CohensD(corpus).set_categories('democrat', ['republican']),
    metadata=convention_df['speaker'],
    grey_threshold=0,
    show_neutral=True
)
file_name = 'demo_cohens_d.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./demo_cohens_d.html in Chrome or Firefox.')
