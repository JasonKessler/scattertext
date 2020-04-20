import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()
convention_df['parse'] = convention_df['text'].apply(st.whitespace_nlp_with_sentences)

topic_model = {
	'money': ['money', 'bank', 'banks', 'finances', 'financial', 'loan', 'dollars', 'income'],
	'jobs': ['jobs', 'workers', 'labor', 'employment', 'worker', 'employee', 'job'],
	'patriotic': ['america', 'country', 'flag', 'americans', 'patriotism', 'patriotic'],
	'family': ['mother', 'father', 'mom', 'dad', 'sister', 'brother', 'grandfather', 'grandmother', 'son', 'daughter']
}
topic_feature_builder = st.FeatsFromTopicModel(topic_model)

topic_corpus = st.CorpusFromParsedDocuments(
	convention_df,
	category_col='party',
	parsed_col='parse',
	feats_from_spacy_doc=topic_feature_builder
).build()

html = st.produce_scattertext_explorer(
	topic_corpus,
	category='democrat',
	category_name='Democratic',
	not_category_name='Republican',
	width_in_pixels=1000,
	metadata=convention_df['speaker'],
	use_non_text_features=True,
	use_full_doc=True,
	pmi_threshold_coefficient=0,
	topic_model_term_lists=topic_feature_builder.get_top_model_term_lists()
)

open('./demo_custom_topic_model.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_custom_topic_model.html in Chrome or Firefox.')
