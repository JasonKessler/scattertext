from sklearn.decomposition import KernelPCA
from sklearn.preprocessing import RobustScaler

import scattertext as st

convention_df = st.SampleCorpora.ConventionData2012.get_data()


corpus = st.CorpusFromPandas(
	convention_df,
	category_col='speaker',
	text_col='text',
	nlp=st.whitespace_nlp_with_sentences
).build().get_unigram_corpus()
html = st.produce_pairplot(corpus, metadata=convention_df['party'] + ': ' + convention_df['speaker'])

file_name = 'convention_pair_plot.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('./' + file_name)
