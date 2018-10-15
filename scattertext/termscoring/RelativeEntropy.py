import numpy as np

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


class RelativeEntropy(CorpusBasedTermScorer):
	'''
	Implements relative entropy approach from
	Peter Fankhauser, Jorg Knappen, Elke Teich. Exploring and visualizing variation in language resources.
	LREC 2014.

	```
	term_scorer = (RelativeEntropy(corpus, smoothing_lambda = 0.05, minimum_p_value=0.05)
		.set_categories('Positive', ['Negative'], ['Plot']))

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
	```
	'''

	def _set_scorer_args(self, **kwargs):
		self.min_p_ = kwargs.get('minimum_p_value', 0.05)
		self.smoothing_lambda_ = kwargs.get('smoothing_lambda', 0.05)

	def get_scores(self, *args):
		'''
		In this case, parameters a and b aren't used, since this information is taken
		directly from the corpus categories.

		Returns
		-------

		'''

		def jelinek_mercer_smoothing(cat):
			p_hat_w = self.tdf_[cat] * 1. / self.tdf_[cat].sum()
			c_hat_w = (self.smoothing_lambda_) * self.tdf_.sum(axis=1) * 1. / self.tdf_.sum().sum()
			return (1 - self.smoothing_lambda_) * p_hat_w + self.smoothing_lambda_ * c_hat_w

		p_w = jelinek_mercer_smoothing('cat')
		q_w = jelinek_mercer_smoothing('ncat')

		kl_divergence = p_w * np.log(p_w / q_w) / np.log(2)

		tt, pvals = self.get_t_statistics()

		return kl_divergence * (pvals < self.min_p_)

	def get_name(self):
		return 'Frankhauser Relative Entropy'
