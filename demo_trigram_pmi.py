import spacy
import scattertext as st

nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

convention_df = st.SampleCorpora.ConventionData2012.get_data().assign(
    Parse=lambda df: [x for x in nlp.pipe(df.text)]
)

corpus = st.CorpusFromParsedDocuments(
    convention_df,
    category_col='party',
    parsed_col='Parse',
    feats_from_spacy_doc=st.FlexibleNGrams(
        ngram_sizes=[1, 2, 3]
    )
).build(
    show_progress=True
).compact(
    compactor=st.NPMICompactor(show_progress=True)
).compact(
    compactor=st.AssociationCompactor(2000)
)

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=convention_df['speaker'],
)

fn = 'trigram_pmi.html'
open(fn, 'w').write(html)
print('open ./' + fn)