from __future__ import print_function

import pandas as pd

from demo import clean_function_factory, iter_party_speech_pairs
from scattertext import CorpusFromParsedDocuments, produce_scattertext_explorer
from scattertext.FastButCrapNLP import fast_but_crap_nlp


def make_political_corpus():
	clean = clean_function_factory()
	data = []
	for party, speech in iter_party_speech_pairs():
		cleaned_speech = clean(speech)
		if cleaned_speech and cleaned_speech != '':
			parsed_speech = fast_but_crap_nlp(cleaned_speech)
			data.append({'party': party,
			             'text': parsed_speech})
	corpus = CorpusFromParsedDocuments(pd.DataFrame(data),
	                                   category_col='party',
	                                   parsed_col='text').build()
	return corpus


def main():
	corpus = make_political_corpus()
	html = produce_scattertext_explorer(corpus,
	                                    category='democrat',
	                                    category_name='Democratic',
	                                    not_category_name='Republican',
	                                    width_in_pixels=1000)
	open('./demo_explorer.html', 'wb').write(html.encode('utf-8'))
	print('Open ./demo_explorer.html in Chrome or Firefox.')
	print("Note: in future version this will show you excerpts of documents that contain the term.")
if __name__ == '__main__':
	main()
