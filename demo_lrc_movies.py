import spacy

from scattertext.Scalers import dense_rank
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments

from scattertext.SampleCorpora import RottenTomatoes
from scattertext import produce_frequency_explorer
from scattertext.termscoring.lrc import LRC

nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

corpus = CorpusFromParsedDocuments(
    RottenTomatoes.get_data().assign(
        Parse=lambda df: df.text.apply(nlp),
        category = lambda df: df.category.apply(
            lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])
    )[lambda df: df.category.isin(['Negative', 'Positive'])],
    category_col='category',
    parsed_col='Parse',
).build().get_unigram_corpus().remove_infrequent_words(5)

term_scorer = LRC(
    corpus=corpus,
).set_categories('Positive', ['Negative']).use_token_counts_as_doc_sizes()
print(corpus.get_df().iloc[0])

html = produce_frequency_explorer(
    corpus,
    category='Positive',
    category_name='Positive',
    not_category_name='Negative',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=lambda c: c.get_df()['movie_name'],
    term_scorer=term_scorer
)

open('./demo_lrc_movies.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_lrc_movies.html in Chrome or Firefox.')

