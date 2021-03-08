import scattertext as st
import spacy
nlp = spacy.load('en_core_web_sm')

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(nlp)
)

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse',
    feats_from_spacy_doc=st.FeatsFromSpacyDoc(use_lemmas=True)
).build().get_unigram_corpus().compact(st.AssociationCompactor(2000))

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0, pmi_threshold_coefficient=0,
    width_in_pixels=1000, metadata=corpus.get_df()['speaker'],
    transform=st.Scalers.dense_rank,
    max_overlapping=3
)
open('./demo_lemmas.html', 'w').write(html)
print('open ./demo_lemmas.html in Chrome')
