from sklearn.decomposition import PCA, FastICA, SparsePCA

import scattertext as st
from scattertext import CategoryProjector, RankDifference, ScaledFScorePresetsNeg1To1
from scattertext.cartegoryprojector.OptimalProjection import get_optimal_category_projection
from scattertext.termcompaction.AssociationCompactor import ScorePercentileCompactor, AssociationCompactor
from scattertext.termscoring import ScaledFScore

movie_df = st.SampleCorpora.RottenTomatoes.get_data()
movie_df.category = movie_df.category \
    .apply(lambda x: {'rotten': 'Negative', 'fresh': 'Positive', 'plot': 'Plot'}[x])

corpus = st.CorpusFromPandas(
    movie_df,
    category_col='movie_name',
    text_col='text',
    nlp=st.whitespace_nlp_with_sentences
).build().get_unigram_corpus()
'''
category_projection = get_optimal_category_projection(
    corpus,
    n_dims=2,
    n_steps=20,
    projector=lambda n_terms, n_dims: CategoryProjector(AssociationCompactor(n_terms, scorer=RankDifference),
                                                        projector=PCA(n_dims)))
'''

html = st.produce_pairplot(corpus,
                           #category_projection=category_projection,
                           metadata=movie_df['category'] + ': ' + movie_df['movie_name'])

file_name = 'movie_pair_plot.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
