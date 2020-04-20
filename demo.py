from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext import SampleCorpora, whitespace_nlp_with_sentences, produce_scattertext_explorer

convention_df = SampleCorpora.ConventionData2012.get_data().assign(
	parse = lambda df: df.text.apply(whitespace_nlp_with_sentences)
)
corpus = CorpusFromParsedDocuments(convention_df, category_col='party', parsed_col='parse').build()

html = produce_scattertext_explorer(
	corpus,
	category='democrat',
	category_name='Democratic',
	not_category_name='Republican',
	minimum_term_frequency=5,
	pmi_threshold_coefficient=8,
	width_in_pixels=1000,
	metadata=convention_df['speaker'],
	d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js',
	d3_url='scattertext/data/viz/scripts/d3.min.js',
)

open('./demo.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo.html in Chrome or Firefox.')
