from __future__ import print_function

import spacy

from scattertext import CorpusFromParsedDocuments, produce_scattertext_explorer
from scattertext import FeatsFromOnlyEmpath
from scattertext import SampleCorpora


def main():
	nlp = spacy.en.English()
	convention_df = SampleCorpora.ConventionData2012.get_data()

	corpus = CorpusFromParsedDocuments(convention_df,
	                                   category_col='party',
	                                   parsed_col='text',
	                                   feats_from_spacy_doc=FeatsFromOnlyEmpath()).build()
	html = produce_scattertext_explorer(corpus,
	                                    category='democrat',
	                                    category_name='Democratic',
	                                    not_category_name='Republican',
	                                    width_in_pixels=1000,
	                                    metadata=convention_df['speaker'],
	                                    use_non_text_features=True,
	                                    use_full_doc=True)
	open('./Convention-Visualization-Empath.html', 'wb').write(html.encode('utf-8'))
	print('Open ./Convention-Visualization-Empath.html in Chrome or Firefox.')


if __name__ == '__main__':
	main()
