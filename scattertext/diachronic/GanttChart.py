import numpy as np
import pandas as pd

from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference


class GanttChart(object):
	'''
	Note: the Gantt charts listed here are inspired by
	Dustin Arendt and Svitlana Volkova. ESTEEM: A Novel Framework for Qualitatively Evaluating and
	Visualizing Spatiotemporal Embeddings in Social Media. ACL System Demonstrations. 2017.
	http://www.aclweb.org/anthology/P/P17/P17-4005.pdf

	In order to use the make chart function, Altair must be installed.
	'''

	def __init__(self,
	             term_doc_matrix,
	             category_to_timestep_func,
	             is_gap_between_sequences_func,
	             timesteps_to_lag=4,
	             num_top_terms_each_timestep=10,
	             num_terms_to_include=40,
	             starting_time_step=None,
	             term_ranker=AbsoluteFrequencyRanker,
	             term_scorer=RankDifference()):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
		category_to_timestep_func : lambda
		is_gap_between_sequences_func : lambda
		timesteps_to_lag : int
		num_top_terms_each_timestep : int
		num_terms_to_include : int
		starting_time_step : object
		term_ranker : TermRanker
		term_scorer : TermScorer
		'''
		self.corpus = term_doc_matrix
		self.timesteps_to_lag = timesteps_to_lag
		self.num_top_terms_each_timestep = num_top_terms_each_timestep
		self.num_terms_to_include = num_terms_to_include
		self.is_gap_between_sequences_func = is_gap_between_sequences_func
		self.category_to_timestep_func = category_to_timestep_func
		self.term_ranker = term_ranker
		self.term_scorer = term_scorer
		categories = list(sorted(self.corpus.get_categories()))
		if len(categories) <= timesteps_to_lag:
			raise Exception("The number of categories in the term doc matrix is <= "
			                + str(timesteps_to_lag))
		if starting_time_step is None:
			starting_time_step = categories[timesteps_to_lag + 1]
		self.starting_time_step = starting_time_step

	def make_chart(self):
		'''
		Returns
		-------
		altair.Chart
		'''
		task_df = self.get_task_df()
		import altair as alt
		chart = alt.Chart(task_df).mark_bar().encode(
			x='start',
			x2='end',
			y='term',
		)
		return chart

	def get_temporal_score_df(self):
		'''
		Returns
		-------

		'''
		scoredf = {}
		tdf = self.term_ranker(self.corpus).get_ranks()
		for cat in sorted(self.corpus.get_categories()):
			if cat >= self.starting_time_step:
				negative_categories = self._get_negative_categories(cat, tdf)
				scores = self.term_scorer.get_scores(
					tdf[cat + ' freq'].astype(int),
					tdf[negative_categories].sum(axis=1)
				)
				scoredf[cat + ' score'] = scores
				scoredf[cat + ' freq'] = tdf[cat + ' freq'].astype(int)
		return pd.DataFrame(scoredf)

	def _get_negative_categories(self, cat, tdf):
		return sorted([x for x in tdf.columns if x < cat])[-self.timesteps_to_lag:]

	def _get_term_time_df(self):
		data = []
		tdf = self.term_ranker(self.corpus).get_ranks()
		for cat in sorted(self.corpus.get_categories()):
			if cat >= self.starting_time_step:
				negative_categories = self._get_negative_categories(cat, tdf)
				scores = self.term_scorer.get_scores(
					tdf[cat + ' freq'].astype(int),
					tdf[negative_categories].sum(axis=1)
				)
				top_term_indices = np.argsort(-scores)[:self.num_top_terms_each_timestep]
				for term in tdf.index[top_term_indices]:
					data.append({'time': self.category_to_timestep_func(cat),
					             'term': term,
					             'top': 1})
		return pd.DataFrame(data)

	def get_task_df(self):
		'''
		Returns
		-------

		'''
		term_time_df = self._get_term_time_df()
		terms_to_include = (
			term_time_df
				.groupby('term')['top']
				.sum()
				.sort_values(ascending=False)
				.iloc[:self.num_terms_to_include].index
		)
		task_df = (
			term_time_df[term_time_df.term.isin(terms_to_include)][['time', 'term']]
				.groupby('term')
				.apply(lambda x: pd.Series(self._find_sequences(x['time'])))
				.reset_index()
				.rename({0: 'sequence'}, axis=1)
				.reset_index()
				.assign(start=lambda x: x['sequence'].apply(lambda x: x[0]))
				.assign(end=lambda x: x['sequence'].apply(lambda x: x[1]))
			[['term', 'start', 'end']]
		)
		return task_df

	def _find_sequences(self, time_steps):
		min_timestep = None
		last_timestep = None
		sequences = []
		cur_sequence = []
		for cur_timestep in sorted(time_steps):
			if min_timestep is None:
				cur_sequence = [cur_timestep]
				min_timestep = cur_timestep
			elif not self.is_gap_between_sequences_func(last_timestep, cur_timestep):
				cur_sequence.append(cur_timestep)
				min_timestep = cur_timestep
			else:
				sequences.append([cur_sequence[0], cur_sequence[-1]])
				cur_sequence = [cur_timestep]
			last_timestep = cur_timestep
		if len(cur_sequence) != []:
			sequences.append([cur_sequence[0], cur_sequence[-1]])
		return sequences
