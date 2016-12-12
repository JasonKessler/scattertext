from scattertext import ScatterChart, percentile_ordinal
from scattertext.Corpus import Corpus
from scattertext.DocsAndLabelsFromCorpus import DocsAndLabelsFromCorpus
import numpy as np


class ScatterChartExplorer(ScatterChart):
	def __init__(self,
	             term_doc_matrix,
	             minimum_term_frequency=3,
	             jitter=0,
	             seed=0,
	             pmi_threshold_coefficient=3,
	             filter_unigrams=False):
		assert isinstance(term_doc_matrix, Corpus)
		ScatterChart.__init__(self,
		                     term_doc_matrix,
		                     minimum_term_frequency,
		                     jitter,
		                     seed,
		                     pmi_threshold_coefficient,
		                     filter_unigrams)

	def to_dict(self,
	            category,
	            category_name=None,
	            not_category_name=None,
	            scores=None,
	            transform=percentile_ordinal):
		'''
		Returns a dictionary that encodes the scatter chart
		information. The dictionary can be dumped as a json document, and
		used in scattertext.html

		:param category: Category to annotate
		:param category_name: Name of category which will appear on web site.
		:param not_category_name: Name of non-category axis which will appear on web site.
		:param scores: Scores to use.  Default to Scaled F-Score.
		:param transform: Defaults to percentile_ordinal
		:return: dictionary {info: {category_name: ..., not_category_name},
												 docs: {'texts': [doc1text, ...], 'labels': [1, 0, ...]}
		                     data: {term:, x:frequency [0-1], y:frequency [0-1],
		                            s: score,
		                            cat25k: freq per 25k in category,
		                            cat: count in category,
		                            ncat: count in non-category,
		                            catdocs: [docnum, ...],
		                            ncatdocs: [docnum, ...]
		                            ncat25k: freq per 25k in non-category}}
		'''

		j = ScatterChart.to_dict(self,
		                        category,
		                        category_name=category_name,
		                        not_category_name=not_category_name,
		                        scores=scores,
		                        transform=percentile_ordinal)
		j['docs'] = DocsAndLabelsFromCorpus(self.term_doc_matrix).get_labels_and_texts()
		return j

	def _add_term_freq_to_json_df(self, json_df, term_freq_df, category):
		ScatterChart._add_term_freq_to_json_df(self, json_df, term_freq_df, category)
		json_df['cat'] = term_freq_df[category + ' freq'].astype(np.int)
		json_df['ncat'] = term_freq_df['not cat freq'].astype(np.int)
