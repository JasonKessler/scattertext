from __future__ import print_function

import scattertext.viz
from scattertext import Scalers, ScatterChart
from scattertext import termranking
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.IndexStore import IndexStore
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.Scalers import percentile_ordinal
from scattertext.ScatterChart import ScatterChart
from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory, FeatsFromDoc
from scattertext.TermDocMatrixFilter import TermDocMatrixFilter, filter_bigrams_by_pmis
from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas
from scattertext.termscoring.ScaledFScore import InvalidScalerException
from scattertext.viz import VizDataAdapter, HTMLVisualizationAssembly
from scattertext import SampleCorpora
from scattertext.ChineseNLP import chinese_nlp

def produce_scattertext_html(term_doc_matrix,
                             category,
                             category_name,
                             not_category_name,
                             protocol='https',
                             pmi_filter_thresold=2,
                             minimum_term_frequency=3,
                             max_terms=None,
                             filter_unigrams=False,
                             height_in_pixels=None,
                             width_in_pixels=None,
                             term_ranker=termranking.AbsoluteFrequencyRanker):
	'''Returns html code of visualization.

	Parameters
	----------
	term_doc_matrix : TermDocMatrix
		Corpus to use
	category : str
		name of category column
	category_name: str
		name of category to mine for
	not_category_name: str
		name of everything that isn't in category
	protocol : str
		optional, used prototcol of , http or https
	filter_unigrams : bool
		default False, do we filter unigrams that only occur in one bigram
	width_in_pixels: int
		width of viz in pixels, if None, default to JS's choice
	height_in_pixels: int
		height of viz in pixels, if None, default to JS's choice
	term_ranker : TermRanker
			TermRanker class for determining term frequency ranks.

	Returns
	-------
		str, html of visualization
	'''
	scatter_chart_data = ScatterChart(term_doc_matrix=term_doc_matrix,
	                                  minimum_term_frequency=minimum_term_frequency,
	                                  pmi_threshold_coefficient=pmi_filter_thresold,
	                                  filter_unigrams=filter_unigrams,
	                                  max_terms=max_terms,
	                                  term_ranker=term_ranker) \
		.to_dict(category=category,
	           category_name=category_name,
	           not_category_name=not_category_name,
	           transform=percentile_ordinal)
	html = HTMLVisualizationAssembly(VizDataAdapter(scatter_chart_data),
	                                 width_in_pixels,
	                                 height_in_pixels).to_html(protocol=protocol)
	return html
from scattertext.termranking import OncePerDocFrequencyRanker

def produce_scattertext_explorer(corpus,
                                 category,
                                 category_name,
                                 not_category_name,
                                 protocol='https',
                                 pmi_filter_thresold=2,
                                 minimum_term_frequency=3,
                                 max_terms=None,
                                 filter_unigrams=False,
                                 height_in_pixels=None,
                                 width_in_pixels=None,
                                 max_snippets=None,
                                 max_docs_per_category=None,
                                 metadata=None,
                                 scores=None,
                                 singleScoreMode=False,
                                 sort_by_dist=True,
                                 use_full_doc=False,
                                 transform=percentile_ordinal,
                                 jitter=0,
                                 grey_zero_scores = False,
                                 term_ranker=termranking.AbsoluteFrequencyRanker,
                                 chinese_mode = False):
	'''Returns html code of visualization.

	Parameters
	----------
	corpus : Corpus
		Corpus to use.
	category : str
		Name of category column as it appears in original data frame.
	category_name : str
		Name of category to use.  E.g., "5-star reviews."
	not_category_name : str
		Name of everything that isn't in category.  E.g., "Below 5-star reviews".
	protocol : str, optional
		Protocol to use.  Either http or https.  Default is https.
	minimum_term_frequency : int, optional
		Minimum number of times word needs to appear to make it into visualization.
	max_terms : int, optional
		Maximum number of terms to include in visualization.
	filter_unigrams : bool, optional
		Default False, do we filter out unigrams that only occur in one bigram
	width_in_pixels : int, optional
		Width of viz in pixels, if None, default to JS's choice
	height_in_pixels : int, optional
		Height of viz in pixels, if None, default to JS's choice
  max_snippets : int, optional
    Maximum number of snippets to show when term is clicked.  If None, all are shown.
  max_docs_per_category: int, optional
    Maximum number of documents to store per category.  If None, by default, all are stored.
	metadata : list, optional
		list of meta data strings that will be included for each document
	scores : np.array, optional
		Array of term scores or None.
	singleScoreMode : bool, optional
		Label terms based on score vs distance from corner.  Good for topic scores. Show only one color.
	sort_by_dist: bool, optional
		Label terms based distance from corner. True by default.  Negated by singleScoreMode.
	use_full_doc : bool, optional
		Use the full document in snippets.  False by default.
	transform : function, optional
		not recommended for editing.  change the way terms are ranked.  default is st.Scalers.percentile_ordinal
	jitter : float, optional
		percentage of axis to jitter each point.  default is 0.
	grey_zero_scores : bool, optional
		If True, color points with zero-scores a light shade of grey.  False by default.
	term_ranker : TermRanker, optional
		TermRanker class for determining term frequency ranks.
	chinese_mode : bool, optional
		Use a special Javascript regular expression that's specific to chinese
	Returns
	-------
		str, html of visualization

	'''
	color = None
	if singleScoreMode:
		color = 'd3.interpolatePurples'
	if singleScoreMode or not sort_by_dist:
		sort_by_dist = False
	else:
		sort_by_dist = True

	scatter_chart_explorer = ScatterChartExplorer(corpus,
	                                              minimum_term_frequency=minimum_term_frequency,
	                                              pmi_threshold_coefficient=pmi_filter_thresold,
	                                              filter_unigrams=filter_unigrams,
	                                              jitter=jitter,
	                                              max_terms=max_terms,
	                                              term_ranker=term_ranker)
	scatter_chart_data = scatter_chart_explorer.to_dict(category=category,
	                                                    category_name=category_name,
	                                                    not_category_name=not_category_name,
	                                                    transform=transform,
	                                                    scores=scores,
	                                                    max_docs_per_category=max_docs_per_category,
	                                                    metadata=metadata)
	return HTMLVisualizationAssembly(VizDataAdapter(scatter_chart_data),
	                                 width_in_pixels=width_in_pixels,
	                                 height_in_pixels=height_in_pixels,
	                                 max_snippets=max_snippets,
	                                 color=color,
	                                 grey_zero_scores=grey_zero_scores,
	                                 sort_by_dist=sort_by_dist,
	                                 use_full_doc=use_full_doc,
	                                 chinese_mode=chinese_mode).to_html(protocol=protocol)
