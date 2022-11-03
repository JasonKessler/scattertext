import pandas as pd
from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.Scalers import dense_rank

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=whitespace_nlp_with_sentences).build()

raw_data = produce_scattertext_explorer(
    corpus,
    category='democrat',
    category_name='Democratic',
    not_category_name='Republican',
    minimum_term_frequency=5,
    pmi_threshold_coefficient=8,
    transform=dense_rank,
    return_data=True,
)
df = pd.DataFrame(raw_data['data'])[['term', 'x', 'y']]
print(df)
