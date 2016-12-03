import numpy as np
import pandas as pd

from scattertext import ScatterChart, percentile_ordinal
from scattertext.Scalers import percentile_min


class ScatterChartExplorer(ScatterChart):
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

		all_categories, other_categories = self._get_category_names(category)
		df = self._build_dataframe_for_drawing(all_categories, category, scores)
		df['x'], df['y'] = self._get_coordinates_from_transform_and_jitter_frequencies \
			(category, df, other_categories, transform)
		doc_id_df = pd.DataFrame(pd.Series(self.term_doc_matrix.term_doc_lists()),
		                         columns=['docids'])
		#print(pd.Series(self.term_doc_matrix.term_doc_lists()))
		df = pd.merge(df, doc_id_df, left_on='term', right_index=True)
		df['not cat freq'] = df[[x for x in other_categories]].sum(axis=1)
		json_df = df[['x', 'y', 'term', 'docids']]
		json_df['cat25k'] = ((df[category + ' freq'] * 1. / df[category + ' freq'].sum()) * 25000)
		json_df['ncat25k'] = ((df['not cat freq'] * 1. / df['not cat freq'].sum()) * 25000)
		json_df['cat25k'] = json_df['cat25k'].apply(np.round).astype(np.int)
		json_df['ncat25k'] = json_df['ncat25k'].apply(np.round).astype(np.int)
		json_df['cat'] = df[category + ' freq']
		json_df['ncat'] = df['not cat freq']
		json_df['s'] = percentile_min(df['color_scores'])
		category_terms = list(json_df.sort_values('s')['term'][:10])
		not_category_terms = list(json_df.sort_values('s')['term'][:10])
		if category_name is None:
			category_name = category
		if not_category_name is None:
			not_category_name = 'Not ' + category_name
		j = {'info': {'category_name': category_name.title(),
		              'not_category_name': not_category_name.title(),
		              'category_terms': category_terms,
		              'not_category_terms': not_category_terms}}
		j['docs'] = {'labels': self.term_doc_matrix._y,
		             'texts': self.term_doc_matrix.get_texts()}
		j['data'] = json_df.sort_values(by=['x', 'y', 'term']).to_dict(orient='records')
		return j