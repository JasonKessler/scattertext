import scattertext as st
import numpy as np

df = st.SampleCorpora.ConventionData2012.get_data().assign(
    parse=lambda df: df.text.apply(st.whitespace_nlp_with_sentences)
).assign(party=lambda df: df['party'].apply({'democrat': 'Democratic',
                                             'republican': 'Republican'}.get))

corpus = st.CorpusFromParsedDocuments(
    df, category_col='party', parsed_col='parse'
).build().get_unigram_corpus()

category_name = 'Democratic'
not_category_name = 'Republican'


def get_log_scale_df(corpus, y_category, x_category):
    term_coord_df = corpus.get_term_freq_df('')

    # Log scale term counts (with a smoothing constant) as the initial coordinates
    coord_columns = []
    for category in [y_category, x_category]:
        col_name = category + '_coord'
        term_coord_df[col_name] = np.log(term_coord_df[category] + 1e-6) / np.log(2)
        coord_columns.append(col_name)

    # Scale these coordinates to between 0 and 1
    min_offset = term_coord_df[coord_columns].min(axis=0).min()
    for coord_column in coord_columns:
        term_coord_df[coord_column] -= min_offset
    max_offset = term_coord_df[coord_columns].max(axis=0).max()
    for coord_column in coord_columns:
        term_coord_df[coord_column] /= max_offset
    return term_coord_df


# Get term coordinates from original corpus
term_coordinates = get_log_scale_df(corpus, category_name, not_category_name)
print(term_coordinates)

# The tooltip JS function. Note that d is is the term data object, and ox and oy are the original x- and y-
# axis counts.
get_tooltip_content = ('(function(d) {return d.term + "<br/>' + not_category_name + ' Count: " ' +
                       '+ d.ox +"<br/>' + category_name + ' Count: " + d.oy})')


html_orig = st.produce_scattertext_explorer(
    corpus,
    category=category_name,
    not_category_name=not_category_name,
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=corpus.get_df()['speaker'],
    show_diagonal=True,
    original_y=term_coordinates[category_name],
    original_x=term_coordinates[not_category_name],
    x_coords=term_coordinates[category_name + '_coord'],
    y_coords=term_coordinates[not_category_name + '_coord'],
    max_overlapping=3,
    use_global_scale=True,
    get_tooltip_content=get_tooltip_content,
)
open('./demo_global_scale_log_orig.html', 'w').write(html_orig)
print('open ./demo_global_scale_log_orig.html in Chrome')

# Select terms which appear a minimum threshold in both corpora
compact_corpus = corpus.compact(st.ClassPercentageCompactor(term_count=2))

# Only take term coordinates of terms remaining in corpus
term_coordinates = term_coordinates.loc[compact_corpus.get_terms()]
print(term_coordinates)


html = st.produce_scattertext_explorer(
    compact_corpus,
    category=category_name,
    not_category_name=not_category_name,
    minimum_term_frequency=0,
    pmi_threshold_coefficient=0,
    width_in_pixels=1000,
    metadata=corpus.get_df()['speaker'],
    show_diagonal=True,
    original_y=term_coordinates[category_name],
    original_x=term_coordinates[not_category_name],
    x_coords=term_coordinates[category_name + '_coord'],
    y_coords=term_coordinates[not_category_name + '_coord'],
    max_overlapping=3,
    use_global_scale=True,
    get_tooltip_content=get_tooltip_content,
)

open('./demo_global_scale_log.html', 'w').write(html)
print('open ./demo_global_scale_log.html in Chrome')
