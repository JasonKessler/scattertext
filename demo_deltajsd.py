from scattertext.Scalers import dense_rank
from scattertext.termscoring.DeltaJSDivergence import DeltaJSDivergence

from scattertext.termcompaction.AssociationCompactor import JSDCompactor

from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_frequency_explorer, RankDifference
from scattertext.CorpusFromPandas import CorpusFromPandas

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(
    convention_df,
    category_col='party',
    text_col='text',
    nlp=whitespace_nlp_with_sentences
).build().get_unigram_corpus().compact(JSDCompactor(1000))

term_etc_df = corpus.get_term_freq_df('').assign(
    DemocraticRank=lambda df: dense_rank(df['democrat']),
    RepublicanRank=lambda df: dense_rank(df['republican']),
    RankDiff=lambda df: RankDifference().get_scores(df['democrat'], df['republican']),
)

get_custom_term_html = '(function(x) {return "Term: " + x.term + "<span class=topic_preview>"' + ' '.join(
    f''' + "<br>{name}: " + x.etc.{key}.toFixed(5)'''
    for name, key in
    [('Democratic Rank', 'DemocraticRank'),
     ('Republican Rank', 'RepublicanRank'),
     ('Rank Difference Score', 'RankDiff')]
) + '+ "</span>" ;})'

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
    term_metadata_df=term_etc_df,
    get_custom_term_html=get_custom_term_html,
    enable_term_category_description=False,
    header_names={'upper': 'Top Dem. RankDiff',
                  'lower': 'Top GOP RankDiff'},
    header_sorting_algos={'upper': '(function(a, b) {return b.etc.RankDiff - a.etc.RankDiff})',
                          'lower': '(function(a, b) {return a.etc.RankDiff - b.etc.RankDiff})'}
)

open('./demo_JSDivergence.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_JSDivergence.html in Chrome or Firefox.')
