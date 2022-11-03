from matplotlib import pyplot as plt

import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)
corpus = st.CorpusFromParsedDocuments(convention_df, category_col='party', parsed_col='parse').build()
scattertext_structure = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=5,
    pmi_threshold_coefficient=8,
    width_in_pixels=1000,
    return_scatterplot_structure=True
)
fig = st.produce_scattertext_pyplot(scattertext_structure)
fig.savefig('pyplot_export.png', format='png')
