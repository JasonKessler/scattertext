from scattertext.Scalers import dense_rank
from scattertext.termscoring.DeltaJSDivergence import DeltaJSDivergence

from scattertext.termcompaction.AssociationCompactor import JSDCompactor

from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_frequency_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(
    convention_df,
    category_col='party',
    text_col='text',
    nlp=whitespace_nlp_with_sentences
).build().get_unigram_corpus().compact(JSDCompactor(1000))

html = produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=convention_df['speaker'],
    term_scorer=DeltaJSDivergence(),
    transform=dense_rank,
    term_metadata_df=corpus.get_term_freq_df(''),
    enable_term_category_description=False
)

open('./demo_JSDivergence.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_JSDivergence.html in Chrome or Firefox.')
