import scattertext as st
from scattertext import LogOddsRatioInformativeDirichletPrior

fn = 'rotten_fresh2.html'
df = st.SampleCorpora.RottenTomatoes.get_data()
corpus = (st.CorpusFromPandas(df,
                              category_col='category',
                              text_col='text',
                              nlp=st.whitespace_nlp_with_sentences)
	.build())
priors = (st.PriorFactory(corpus,
                          category='fresh',
                          not_categories=['rotten'],
                          starting_count=1)
	.use_general_term_frequencies()
	.use_all_categories()
	.get_priors())
(open(fn, 'wb')
	.write(
	st.produce_fightin_words_explorer(
		corpus,
		category='fresh',
		not_categories=['rotten'],
		metadata=df['movie_name'],
		term_scorer=LogOddsRatioInformativeDirichletPrior(priors, alpha_w=10),
	).encode('utf-8'))
)
print(fn)
