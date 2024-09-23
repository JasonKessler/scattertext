import re

import scattertext as st
import pandas as pd
from tqdm.auto import tqdm
import spacy

tqdm.pandas()

nlp = spacy.load('en_core_web_sm')

convention_df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(nlp),
    party=lambda df: df.party.apply({'democrat': 'Democratic', 'republican': 'Republican'}.get)
)

word_number_matcher = re.compile('^[A-Za-z0-9 ]+$')


def exclude_ngrams_which_do_not_start_and_end_with_function_words(ngram: spacy.tokens.Span) -> bool:
    return any([
        ngram[0].lower_.strip() in st.MY_ENGLISH_STOP_WORDS,
        ngram[-1].lower_.strip() in st.MY_ENGLISH_STOP_WORDS,
        word_number_matcher.match(ngram[0].lower_.strip()) is None,
        word_number_matcher.match(ngram[-1].lower_.strip()) is None
    ])


offset_corpus = st.OffsetCorpusFactory(
    convention_df[lambda df: df.party == 'Democratic'],
    category_col='speaker',
    parsed_col='parse',
    feat_and_offset_getter=st.FlexibleNGramFeatures(
        ngram_sizes=[1, 2, 3, 4, 5, 6, 7, 8],
        text_from_token=lambda tok: tok.lemma_ if tok.orth_.lower() not in st.MY_ENGLISH_STOP_WORDS else tok.orth_,
        exclude_ngram_filter=exclude_ngrams_which_do_not_start_and_end_with_function_words,
        whitespace_substitute='_'
    )
).build().compact(
    compactor=st.NPMICompactor(
        minimum_term_count=3,
        number_terms_per_length=3000,
        token_split_function=lambda x: x.split('_'),
        token_join_function=lambda x: '_'.join(x)
    ),
    non_text=True
).compact(
    st.NgramPercentageCompactor(
        usage_portion=0.5,
        minimum_term_count=1,
        token_split_function=lambda x: x.split('_'),
        token_join_function=lambda x: '_'.join(x)
    ),
    non_text=True
).filter_out(
    lambda x: len(x) == 1,
    non_text=True
).compact(
    compactor=st.AssociationCompactor(
        3000,
        scorer=st.HedgesG,
        use_non_text_features=True,
        include_n_most_frequent_terms=20,
    ),
    non_text=True
)

dispersion = st.Dispersion(offset_corpus, use_categories_as_documents=True, non_text=True)
dispersion_df = dispersion.get_df(include_da=True)

print("Top 10 most disseminated terms")
print(dispersion_df.sort_values(by="Dissemination", ascending=False).head(10))

print("Top 10 least disseminated terms")
print(dispersion_df.sort_values(by="Dissemination", ascending=True).head(10))

plot_df = dispersion_df.assign(
    X=lambda df: df.Frequency,
    Xpos=lambda df: st.Scalers.dense_rank(df.X),
    Y=lambda df: df.Dissemination,
    Ypos=lambda df: st.scale(df.Y),
    Color='#ffbf00'
)

line_coordinates = pd.DataFrame({
    'x': plot_df.Xpos.values,
    'y': (1 - plot_df.Y.min())/(plot_df.Y.max() - plot_df.Y.min()) ,
}).sort_values(by='x').to_dict('records')

html = st.dataframe_scattertext(
    offset_corpus,
    plot_df=plot_df,
    metadata=lambda corpus: corpus.get_df()['speaker'],
    unified_context=True,
    use_full_doc=True,
    use_non_text_features=True,
    use_offsets=True,
    x_label='Frequency Rank',
    y_label='Dissemination',
    y_axis_labels=['Concentrated', 'Medium', 'Dispersed'],
    color_column='Color',
    tooltip_columns=['Frequency', 'Dissemination'],
    header_names={'upper': f'Most Disseminated', 'lower': f'Least Disseminated'},
    left_list_column='Dissemination',
    line_coordinates=line_coordinates
)

file_name = 'demo_dissemination_republicans.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open ./%s in Chrome.' % (file_name))
