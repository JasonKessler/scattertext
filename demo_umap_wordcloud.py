import re

import numpy as np
import pandas as pd
import umap

import scattertext as st
import spacy

nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

movie_full_df = st.SampleCorpora.RottenTomatoes.get_data().assign(
    category=lambda df: df.category.apply(
        lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x]),
    SpacyParse=lambda df: df.text.apply(nlp)
)
movie_df = movie_full_df[lambda df: df.category.isin(['Negative', 'Positive'])]

stoplist_corpus = st.CorpusFromParsedDocuments(
    movie_df,
    category_col='category',
    parsed_col='SpacyParse',
    feats_from_spacy_doc=st.FlexibleNGrams(ngram_sizes=[1])
).build().filter_out(
    lambda x: len(x.strip()) < 1
).remove_terms_used_in_less_than_num_docs(
    threshold=6
).get_stoplisted_corpus().filter_out(
    lambda x: re.match('^[A-Za-z]+$', x) is None
)

model = st.Word2VecFromParsedCorpus(
    stoplist_corpus
).train()
embeddings = np.array([model.wv[w] for w in stoplist_corpus.get_terms()]).T
projection_raw = umap.UMAP(min_dist=0.5, metric='cosine').fit_transform(embeddings.T)

plot_df = pd.DataFrame({
    'term': stoplist_corpus.get_terms(),
    'X': projection_raw.T[0],
    'Y': projection_raw.T[1],
    'Frequency': stoplist_corpus.get_term_freq_df().sum(axis=1),
}).set_index('term').assign(
    XPos=lambda df: st.scale(df.X),
    YPos=lambda df: st.scale(df.Y),
    LRC=st.LRC(
        stoplist_corpus,
        conf_level=0.8
    ).set_categories('Positive', ['Negative']).get_scores(),
    TextColor=lambda df: st.get_ternary_colors(df.LRC.values,
                                               negative_color="#d72d00",
                                               zero_color="#bdbdbd",
                                               positive_color="#2a3e63"),
    TextSize=lambda df: st.scale_font_size(df.Frequency, min_size=9, max_size=15),
    LabelOrder=lambda df: np.abs(df.LRC)
)


def get_heading(corpus: st.ParsedCorpus) -> str:
    return corpus.get_df().movie_name


html = st.dataframe_scattertext(
    stoplist_corpus,
    category='Positive',
    category_name='Positive',
    not_category_name='Negative',
    text_color_column='TextColor',
    color_column='TextColor',
    text_size_column='TextSize',
    label_priority_column='LabelOrder',
    plot_df=plot_df,
    metadata=get_heading,
    ignore_categories=False,
    use_full_doc=True,
    x_label='UMAP 0',
    y_label='UMAP 1',
    tooltip_columns=['LRC', 'Frequency'],
    show_top_terms=False,
    show_characteristic=False,
    suppress_circles=True,
    center_label_over_points=True
)
fn = 'demo_movie_wordcloud.html'
with open(fn, 'wb') as of:
    of.write(('<h2>UMAP Projection of Skip-gram Embeddings</h2>' + html).encode('utf-8'))
print(f'./open {fn}')
