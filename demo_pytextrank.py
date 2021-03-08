from scattertext import SampleCorpora, RankDifference, dense_rank, PyTextRankPhrases, AssociationCompactor, \
    produce_scattertext_explorer
from scattertext import CorpusFromParsedDocuments
import spacy
import numpy as np
import pytextrank

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("textrank", last=True)

convention_df = SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(nlp),
    party=lambda df: df.party.apply({'democrat': 'Democratic', 'republican': 'Republican'}.get)
)

corpus = CorpusFromParsedDocuments(
    convention_df,
    category_col='party',
    parsed_col='parse',
    feats_from_spacy_doc=PyTextRankPhrases()
).build(
).compact(
    AssociationCompactor(2000, use_non_text_features=True)
)

print('Aggregate PyTextRank phrase scores')
term_category_scores = corpus.get_metadata_freq_df('')
print(term_category_scores)

term_ranks = np.argsort(np.argsort(-term_category_scores, axis=0), axis=0) + 1

metadata_descriptions = {
    term: '<br/>' + '<br/>'.join(
        '<b>%s</b> TextRank score rank: %s/%s' % (cat, term_ranks.loc[term, cat], corpus.get_num_metadata())
        for cat in corpus.get_categories())
    for term in corpus.get_metadata()
}

category_specific_prominence = term_category_scores.apply(
    lambda r: r.Democratic if r.Democratic > r.Republican else -r.Republican,
    axis=1
)

html = produce_scattertext_explorer(
    corpus,
    category='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    transform=dense_rank,
    use_non_text_features=True,
    metadata=corpus.get_df()['speaker'],
    scores=category_specific_prominence,
    sort_by_dist=False,
    # ensure that we search for term in visualization
    topic_model_term_lists={term: [term] for term in corpus.get_metadata()},
    topic_model_preview_size=0,  # ensure singleton topics aren't shown
    metadata_descriptions=metadata_descriptions,
    use_full_doc=True
)

file_name = 'demo_pytextrank_prominence.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)

html = produce_scattertext_explorer(
    corpus,
    category='Democratic',
    not_category_name='Republican',
    width_in_pixels=1000,
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    transform=dense_rank,
    use_non_text_features=True,
    metadata=corpus.get_df()['speaker'],
    term_scorer=RankDifference(),
    topic_model_term_lists={term: [term] for term in corpus.get_metadata()},
    topic_model_preview_size=0,  # ensure singleton topics aren't shown
    metadata_descriptions=metadata_descriptions,
    use_full_doc=True
)

file_name = 'demo_pytextrank_rankdiff.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)
