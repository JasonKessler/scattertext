import numpy as np

import scattertext as st
import scipy.stats as ss
import pandas as pd

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
)

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse'
).build().get_unigram_corpus().remove_terms_used_in_less_than_num_docs(
    threshold=6
)


metric = 'DA'

plot_df = st.dispersion_ranker_factory(
    metric = metric,
    corpus_to_parts = lambda x: x.get_df()['speaker']
)(
    term_doc_matrix=corpus
).get_ranks(label_append='').assign(
    X=lambda df: df.democrat,
    Y=lambda df: df.republican,
    RepRank = lambda df: ss.rankdata(df.X, method='dense'),
    DemRank = lambda df: ss.rankdata(df.Y, method='dense'),
    Xpos=lambda df: st.scale(df.NegRank),
    Ypos=lambda df: st.scale(df.PosRank),
    ColorScore=lambda df: st.Scalers.scale_center_zero(df.Ypos - df.Xpos),
)


line_df = pd.DataFrame({
    'x': np.arange(0, 1, 0.01),
    'y': np.arange(0, 1, 0.01),
})


html = st.dataframe_scattertext(
    corpus,
    plot_df=plot_df,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    width_in_pixels=1000,
    ignore_categories=False,
    metadata=lambda x: x.get_df()['speaker'],
    color_score_column='ColorScore',
    left_list_column='ColorScore',
    show_characteristic=False,
    y_label=f'Positive {metric}',
    x_label=f'Negative {metric}',
    tooltip_columns=['DemRank', 'RepRank'],
    header_names={'upper': f'Top Democratic {metric}', 'lower': f'Top Republican {metric}'},
    line_coordinates = line_df.to_dict('records'),
)

fn = f''
with open(fn, 'w') as of:
    of.write(html)


