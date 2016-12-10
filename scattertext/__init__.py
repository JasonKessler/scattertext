from __future__ import print_function

import scattertext.viz
from scattertext import Scalers, ScatterChart
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.FastButCrapNLP import fast_but_crap_nlp
from scattertext.IndexStore import IndexStore
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.Scalers import percentile_ordinal
from scattertext.ScatterChart import ScatterChart
from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.TermDocMatrix import TermDocMatrix, InvalidScalerException
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory, FeatsFromDoc
from scattertext.TermDocMatrixFilter import TermDocMatrixFilter, filter_bigrams_by_pmis
from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas
from scattertext.viz import VizDataAdapter, HTMLVisualizationAssembly


def produce_scattertext_html(term_doc_matrix,
                             category,
                             category_name,
                             not_category_name,
                             protocol='https',
                             pmi_filter_thresold=2,
                             minimum_term_frequency=3,
                             filter_unigrams=False,
                             height_in_pixels=None,
                             width_in_pixels=None):
	'''
	Parameters
	----------
	term_doc_matrix TermDocMatrix
	category, str: name of category column
	category_name, str: name of category to mine for
	not_category_name, str: name of everything that isn't in category
	protocol, str, optional, used prototcol of , http or https
	filter_unigrams: bool, default False, do we filter unigrams that only occur in one bigram
	param width_in_pixels: int, width of viz in pixels, if None, default to JS's choice
	param height_in_pixels: height, width of viz in pixels, if None, default to JS's choice

	Returns
	-------
	str, html of visualization
	'''
	scatter_chart = ScatterChart(term_doc_matrix=term_doc_matrix,
	                             minimum_term_frequency=minimum_term_frequency,
	                             pmi_threshold_coefficient=pmi_filter_thresold,
	                             filter_unigrams=filter_unigrams)
	scatter_chart_data = scatter_chart.to_dict(category=category,
	                                           category_name=category_name,
	                                           not_category_name=not_category_name,
	                                           transform=percentile_ordinal)
	viz_data_adapter = VizDataAdapter(scatter_chart_data)
	html = HTMLVisualizationAssembly(viz_data_adapter,
	                                 width_in_pixels,
	                                 height_in_pixels).to_html(protocol=protocol)
	return html


def produce_scattertext_explorer(corpus,
                                 category,
                                 category_name,
                                 not_category_name,
                                 protocol='https',
                                 pmi_filter_thresold=2,
                                 minimum_term_frequency=3,
                                 filter_unigrams=False,
                                 height_in_pixels=None,
                                 width_in_pixels=None):
	'''
	Parameters
	----------
	corpus corpus
	category, str: name of category column
	category_name, str: name of category to mine for
	not_category_name, str: name of everything that isn't in category
	protocol, str, optional, used prototcol of , http or https
	filter_unigrams: bool, default False, do we filter unigrams that only occur in one bigram
	param width_in_pixels: int, width of viz in pixels, if None, default to JS's choice
	param height_in_pixels: height, width of viz in pixels, if None, default to JS's choice

	Returns
	-------
	str, html of visualization
	'''
	scatter_chart = ScatterChartExplorer(corpus,
	                                     minimum_term_frequency=minimum_term_frequency,
	                                     pmi_threshold_coefficient=pmi_filter_thresold,
	                                     filter_unigrams=filter_unigrams)
	scatter_chart_data = scatter_chart.to_dict(category=category,
	                                           category_name=category_name,
	                                           not_category_name=not_category_name,
	                                           transform=percentile_ordinal)
	viz_data_adapter = VizDataAdapter(scatter_chart_data)
	html = HTMLVisualizationAssembly(viz_data_adapter,
	                                 width_in_pixels,
	                                 height_in_pixels).to_html(protocol=protocol)
	return html
