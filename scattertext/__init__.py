from __future__ import print_function

import scattertext.viz
from scattertext import Scalers, ScatterChart
from scattertext.CSRMatrixTools import CSRMatrixFactory
#from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.FastButCrapNLP import fast_but_crap_nlp
from scattertext.IndexStore import IndexStore
from scattertext.Scalers import percentile_ordinal
from scattertext.ScatterChart import ScatterChart
from scattertext.TermDocMatrix import TermDocMatrix, InvalidScalerException
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory, FeatsFromDoc
from scattertext.TermDocMatrixFilter import TermDocMatrixFilter, filter_bigrams_by_pmis
from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas
from scattertext.viz import VizDataAdapter, HTMLVisualizationAssembly


def produce_scattertext_html(term_doc_matrix, category, category_name, not_category_name):
	scatter_chart = ScatterChart(term_doc_matrix=term_doc_matrix)
	scatter_chart_data = scatter_chart.to_dict(category=category,
	                                           category_name=category_name,
	                                           not_category_name=not_category_name,
	                                           transform=percentile_ordinal)
	viz_data_adapter = VizDataAdapter(scatter_chart_data)
	html = HTMLVisualizationAssembly(viz_data_adapter).to_html()
	return html
