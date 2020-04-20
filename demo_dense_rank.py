from scattertext.Scalers import dense_rank

from scattertext.termscoring.RankDifference import RankDifference

from scattertext.termcompaction.AssociationCompactor import AssociationCompactor

from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(
    convention_df,
    category_col='party',
    text_col='text',
    nlp=whitespace_nlp_with_sentences
).build().get_unigram_corpus().compact(AssociationCompactor(4000))

html = produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=convention_df['speaker'],
    term_scorer=RankDifference(),
    transform=dense_rank
)

open('./demo_dense_rank.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_dense_rank.html in Chrome or Firefox.')
