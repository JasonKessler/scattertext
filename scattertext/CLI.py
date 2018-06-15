import argparse

import pandas as pd

from scattertext import CorpusFromPandas, produce_scattertext_explorer, Common
from scattertext.WhitespaceNLP import whitespace_nlp_with_sentences
from scattertext.termranking import OncePerDocFrequencyRanker


def main():
	parser = argparse.ArgumentParser(description="A primitive, incomplete commandline interface to Scattertext.")
	parser.add_argument('--datafile', action='store', dest='datafile', required=True,
	                    help="Path (or URL) of a CSV file with at least two columns."
	                         "Text and category column names are indicated by the --text_column"
	                         "and --category_column arguments.  By default, they are 'text', and 'category'. "
	                         "Optionally, a metadata "
	                         "column (named in the --metadata argument) can be present. ")
	parser.add_argument('--outputfile', action='store', dest='outputfile', default="-",
	                    help="Path of HTML file on which to store visualization. Pass in - (default) for stdout.")
	parser.add_argument('--text_column', action='store', dest='text_column', default="text",
	                    help="Name of the text column.")
	parser.add_argument('--category_column', action='store', dest='category_column', default="category",
	                    help="Name of the category column.")
	parser.add_argument('--metadata_column', action='store', dest='metadata_column', default=None,
	                    help="Name of the category column.")
	parser.add_argument('--positive_category', action='store', required=True,
	                    dest='positive_category',
	                    help="Postive category.  A value in category_column to be considered the positive class. "
	                         "All others will be considered negative.")
	parser.add_argument('--category_display_name', action='store',
	                    dest='category_display_name', default=None,
	                    help="Positive category name which will "
	                         "be used on the visualization. By default, it will just be the"
	                         "postive category value.")
	parser.add_argument('--not_category_display_name', action='store', default=None,
	                    dest='not_category_display_name',
	                    help="Positive category name which will "
	                         "be used on the visualization. By default, it will just be the word 'not' "
	                         "in front of the positive value.")
	parser.add_argument('--pmi_threshold', action='store',
	                    dest='pmi_threshold', type=int,
	                    help="2 * minimum allowable PMI value.  Default 6.")
	parser.add_argument('--width_in_pixels', action='store',
	                    dest='width_in_pixels', type=int, default=1000,
	                    help="Width of the visualization in pixels.")
	parser.add_argument('--minimum_term_frequency', action='store',
	                    dest='minimum_term_frequency', type=int, default=3,
	                    help="Minimum number of times a term needs to appear. Default 3")
	parser.add_argument('--regex_parser', action='store_true',
	                    dest='regex_parser', default=False,
	                    help="If present, don't use spaCy for preprocessing.  Instead, "
	                         "use a simple, dumb, regex.")
	parser.add_argument('--spacy_language_model', action='store',
	                    dest='spacy_language_model', default='en',
	                    help="If present, pick the spaCy language model to use. Default is 'en'. "
	                         "Other valid values include 'de' and 'fr'. --regex_parser will override."
	                         "Please see https://spacy.io/docs/api/language-models for moredetails")
	parser.add_argument('--one_use_per_doc', action='store_true',
	                    dest='one_use_per_doc', default=False,
	                    help="Only count one use per document.")
	args = parser.parse_args()
	df = pd.read_csv(args.datafile)

	if args.category_column not in df.columns:
		raise Exception("category_column (%s) must be a column name in csv. Must be one of %s"
		                % (args.category_column, ', '.join(df.columns)))
	if args.text_column not in df.columns:
		raise Exception("text_column (%s) must be a column name in csv. Must be one of %s"
		                % (args.text_column, ', '.join(df.columns)))
	if args.metadata_column is not None and args.metadata_column not in df.columns:
		raise Exception("metadata_column (%s) must be a column name in csv. Must be one of %s"
		                % (args.metadata_column, ', '.join(df.columns)))
	if args.positive_category not in df[args.category_column].unique():
		raise Exception("positive_category (%s) must be in the column ""%s"", with a case-sensitive match." %
		                (args.positive_category, args.category_column))
	if args.regex_parser:
		nlp = whitespace_nlp_with_sentences
	else:
		import spacy
		nlp = spacy.load(args.spacy_language_model)

	term_ranker = None
	if args.one_use_per_doc is True:
		term_ranker = OncePerDocFrequencyRanker

	category_display_name = args.category_display_name
	if category_display_name is None:
		category_display_name = args.positive_category
	not_category_display_name = args.not_category_display_name
	if not_category_display_name is None:
		not_category_display_name = 'Not ' + category_display_name

	corpus = CorpusFromPandas(df,
	                          category_col=args.category_column,
	                          text_col=args.text_column,
	                          nlp=nlp).build()
	html = produce_scattertext_explorer(corpus,
	                                    category=args.positive_category,
	                                    category_name=category_display_name,
	                                    not_category_name=not_category_display_name,
	                                    minimum_term_frequency=args.minimum_term_frequency,
	                                    pmi_filter_thresold=args.pmi_threshold,
	                                    width_in_pixels=args.width_in_pixels,
	                                    term_ranker=term_ranker,
	                                    metadata=None if args.metadata_column is None \
		                                    else df[args.metadata_column]
	                                    )
	if args.outputfile == '-':
		print(html)
	else:
		with open(args.outputfile, 'wb') as o:
			o.write(html.encode('utf-8'))


if __name__ == '__main__':
	main()
