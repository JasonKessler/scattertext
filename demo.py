from scattertext import SampleCorpora, whitespace_nlp_with_sentences, RankDifference
from scattertext import produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=whitespace_nlp_with_sentences).build()

html = produce_scattertext_explorer(
	corpus,
	category='democrat',
	category_name='Democratic',
	not_category_name='Republican',
	minimum_term_frequency=5,
	pmi_threshold_coefficient=8,
	width_in_pixels=1000,
	metadata=convention_df['speaker'],
	term_scorer=RankDifference(),
	d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
	d3_url='scattertext/data/viz/scripts/d3.min.js'
)

open('./demo.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo.html in Chrome or Firefox.')
