import numpy as np

from scattertext import ScatterChart
from scattertext import percentile_alphabetical
from scattertext.Corpus import Corpus
from scattertext.DocsAndLabelsFromCorpus import DocsAndLabelsFromCorpus, DocsAndLabelsFromCorpusSample


class ScatterChartExplorer(ScatterChart):
	def __init__(self,
	             corpus,
	             **kwargs):
		'''See ScatterChart.  This lets you click on terms to see what contexts they tend to appear in.

		'''
		assert isinstance(corpus, Corpus)
		ScatterChart.__init__(self, corpus, **kwargs)

	def to_dict(self,
	            category,
	            category_name=None,
	            not_category_name=None,
	            scores=None,
	            metadata=None,
	            max_docs_per_category=None,
	            transform=percentile_alphabetical):
		'''
		:param category: Category to annotate
		:param category_name: Name of category which will appear on web site.
		:param not_category_name: Name of non-category axis which will appear on web site.
		:param scores: Scores to use.  Default to Scaled F-Score.
		:param metadata: None or array-like.  List of metadata for each document.
		:param max_docs_per_category: None or int.  Maximum number of documents to store per category.
		:param transform: Defaults to percentile_lexicographic
		:return: dictionary {info: {category_name: ..., not_category_name},
												 docs: {'texts': [doc1text, ...],
												        'labels': [1, 0, ...],
												        'meta': ['<b>blah</b>', '<b>blah</b>']}
		                     data: {term:, x:frequency [0-1], y:frequency [0-1],
		                            s: score,
		                            bg: background score,
		                            as: association score,
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
		                         transform=transform)
		docs_getter = self._make_docs_getter(max_docs_per_category)
		j['docs'] = self._get_docs_structure(docs_getter, metadata)
		return j

	def _make_docs_getter(self, max_docs_per_category):
		if max_docs_per_category is None:
			docs_getter = DocsAndLabelsFromCorpus(self.term_doc_matrix)
		else:
			docs_getter = DocsAndLabelsFromCorpusSample(self.term_doc_matrix, max_docs_per_category)
		if self.scatterchartdata.use_non_text_features:
			docs_getter = docs_getter.use_non_text_features()
		return docs_getter

	def _get_docs_structure(self, docs_getter, metadata):
		if metadata is not None:
			return docs_getter.get_labels_and_texts_and_meta(np.array(metadata))
		else:
			return docs_getter.get_labels_and_texts()

	def _add_term_freq_to_json_df(self, json_df, term_freq_df, category):
		ScatterChart._add_term_freq_to_json_df(self, json_df, term_freq_df, category)
		json_df['cat'] = term_freq_df[category + ' freq'].astype(np.int)
		json_df['ncat'] = term_freq_df['not cat freq'].astype(np.int)
