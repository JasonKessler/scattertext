from scattertext.Common import MY_ENGLISH_STOP_WORDS

import scattertext as st
import spacy

nlp = spacy.load('en_core_web_sm')

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse = lambda df: df.text.apply(nlp)
)

corpus = st.OffsetCorpusFactory(
    df,
    category_col='party',
    parsed_col='parse',
    feat_and_offset_getter=st.FlexibleNGramFeatures(
        ngram_sizes=[1, 2, 3],
        text_from_token=(
            lambda tok: (tok.tag_
                         if (tok.lower_ not in MY_ENGLISH_STOP_WORDS
                             or tok.tag_[:2] in ['VB', 'NN', 'JJ', 'RB', 'FW'])
                         else tok.lower_)
        ),
        validate_token=lambda tok: tok.tag_ != '_SP'
    )
).build().compact(st.AssociationCompactor(2000, use_non_text_features=True), non_text=True)

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Repubican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=corpus.get_df()['speaker'],
    use_offsets=True,
    use_non_text_features=True,
    show_diagonal=False,
)
open('./demo_stylistic_features.html', 'w').write(html)
print('open ./demo_stylistic_features.html in Chrome')



