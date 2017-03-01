import spacy

from scattertext import SampleCorpora, word_similarity_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas


def main():
	nlp = spacy.en.English()
	convention_df = SampleCorpora.ConventionData2012.get_data()
	corpus = CorpusFromPandas(convention_df,
	                          category_col='party',
	                          text_col='text',
	                          nlp=nlp).build()
	html = word_similarity_explorer(corpus,
	                                category='democrat',
	                                category_name='Democratic',
	                                not_category_name='Republican',
	                                target_term='jobs',
	                                minimum_term_frequency=5,
	                                pmi_filter_thresold=4,
	                                width_in_pixels=1000,
	                                metadata=convention_df['speaker'],
	                                alpha=0.01,
	                                max_p_val=0.05,
	                                save_svg_button=True)
	open('./demo_similarity.html', 'wb').write(html.encode('utf-8'))
	print('Open ./demo_similarlity.html in Chrome or Firefox.')


if __name__ == '__main__':
	main()
