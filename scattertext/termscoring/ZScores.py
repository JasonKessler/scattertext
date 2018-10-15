import pandas as pd

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class ZScores(CorpusBasedTermScorer):
	'''
	Z-scores from Welch's t-test

	term_scorer = (ZScores(corpus).set_categories('Positive', ['Negative'], ['Plot']))

	html = st.produce_frequency_explorer(
		corpus,
		category='Positive',
		not_categories=['Negative'],
		neutral_categories=['Plot'],
		term_scorer=term_scorer,
		metadata=rdf['movie_name'],
		grey_threshold=0,
		show_neutral=True
	)
	file_name = 'rotten_fresh_fre.html'
	open(file_name, 'wb').write(html.encode('utf-8'))
	IFrame(src=file_name, width=1300, height=700)
	'''

	def _set_scorer_args(self, **kwargs):
		pass

	def get_scores(self, *args):
		return pd.Series(self.get_t_statistics()[0],
						 index=self._get_index())

	def get_name(self):
		return "Z-Score from Welch's T-Test"
