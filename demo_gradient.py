import numpy as np

import scattertext as st
import matplotlib.pyplot as plt
import matplotlib as mpl

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse'
).build().get_unigram_corpus().compact(st.AssociationCompactor(2000))

html = st.produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=corpus.get_df()['speaker'],
    transform=st.Scalers.dense_rank,
    include_gradient=True,
    left_gradient_term="More Democratic",
    right_gradient_term="More Republican",
    middle_gradient_term='Metric: Dense Rank Difference',
    gradient_text_color="white",
    term_colors=dict(zip(
        corpus.get_terms(),
        [
            mpl.colors.to_hex(x) for x in plt.get_cmap('brg')(
                st.Scalers.scale_center_zero_abs(
                    st.RankDifferenceScorer(corpus).set_categories('democrat').get_scores()).values
            )
        ]
    )),
    gradient_colors=[mpl.colors.to_hex(x) for x in plt.get_cmap('brg')(np.arange(1., 0., -0.01))],
)
open('./demo_gradient.html', 'w').write(html)
print('open ./demo_gradient.html in Chrome')