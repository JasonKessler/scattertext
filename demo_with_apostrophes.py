import scattertext as st
import spacy

nlp = spacy.blank('en_core_web_sm')
nlp.tokenizer.rules = {key: value for key, value in nlp.tokenizer.rules.items()
                       if "'" not in key and "’" not in key and "‘" not in key}
nlp.add_pipe(nlp.create_pipe('sentencizer'))

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(nlp)
)

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse'
).build().compact(st.ClassPercentageCompactor(term_count=10))

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0, pmi_threshold_coefficient=0,
    width_in_pixels=1000, metadata=corpus.get_df()['speaker'],
    transform=st.Scalers.dense_rank,
    show_diagonal=False,
    max_overlapping=3
)
open('./demo_with_apostrophes.html', 'w').write(html)
print('open ./demo_with_apostrophes.html in Chrome')
