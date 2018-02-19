from scattertext.termcompaction.CompactTerms import CompactTerms

import scattertext as st
from scattertext import LogOddsRatioInformativeDirichletPrior

fn = 'demo_log_odds_ratio_prior.html'
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
          #.use_general_term_frequencies()
          .use_all_categories()
          .get_priors())
(open(fn, 'wb')
	.write(
	st.produce_frequency_explorer(
		corpus,
		category='fresh',
		not_categories=['rotten'],
		metadata=df['movie_name'],
		term_scorer=LogOddsRatioInformativeDirichletPrior(priors, 1),
	).encode('utf-8'))
)
print(fn)

CompactTerms