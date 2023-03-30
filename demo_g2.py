
import spacy

from scattertext.Scalers import dense_rank, scale
from scattertext.termscoring.g2 import G2
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments

from scattertext.SampleCorpora import ConventionData2012
from scattertext import produce_frequency_explorer

nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

corpus = CorpusFromParsedDocuments(
    ConventionData2012.get_data().assign(
        Parse=lambda df: df.text.apply(nlp)
    ),
    category_col='party',
    parsed_col='Parse',
).build().get_unigram_corpus().remove_infrequent_words(5)

term_scorer = G2(
    corpus=corpus,
).set_categories('democrat', ['republican']).use_token_counts_as_doc_sizes()

html = produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=lambda c: c.get_df()['speaker'],
    term_scorer=term_scorer,
    frequency_transform=dense_rank,
    transform=dense_rank,
    score_scaler=dense_rank
)

open('./demo_g2.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_g2.html in Chrome or Firefox.')


alpha = 0.05
term_scorer = G2(
    corpus=corpus,
    alpha=alpha,
    correct=True
).set_categories('democrat', ['republican']).use_token_counts_as_doc_sizes()

html = produce_frequency_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=lambda c: c.get_df()['speaker'],
    term_scorer=term_scorer,
    frequency_transform=dense_rank,
    transform=dense_rank,
    score_scaler=dense_rank
)

print(term_scorer.get_score_df())

fn = f'demo_g2_alpha_{alpha}.html'

open(f'./{fn}', 'wb').write(html.encode('utf-8'))
print(f'Open ./{fn} in Chrome or Firefox.')
