import matplotlib.pyplot as plt
import numpy as np
# from adjustText import adjust_text
from mpld3 import plugins, fig_to_html
from statsmodels.distributions.empirical_distribution import ECDF
from scipy.stats import rankdata


def filter_bigrams_by_pmis(word_freq_df, threshold_coef=2):
	is_bigram = np.array([' ' in word for word in word_freq_df.index])
	unigram_freq = word_freq_df[~is_bigram].sum(axis=1)
	bigram_freq = word_freq_df[is_bigram].sum(axis=1)
	bigram_prob = bigram_freq / bigram_freq.sum()
	unigram_prob = unigram_freq / unigram_freq.sum()

	def get_pmi(bigram):
		return np.log(
			bigram_prob[bigram] / np.product([unigram_prob[word] for word in bigram.split(' ')])
		) / np.log(2)

	low_pmi_bigrams = bigram_prob[bigram_prob.index.map(get_pmi) < threshold_coef * 2]
	return word_freq_df.drop(low_pmi_bigrams.index)


class Scalers:
	@staticmethod
	def scale(vec):
		return (vec - vec.min()) / (vec.max() - vec.min())

	@staticmethod
	def scale_standardize(vec):
		to_ret = (vec - vec.mean()) / vec.std()
		to_ret += to_ret.min() + 1
		# to_ret = np.log(to_ret)/np.log(2)
		to_ret += to_ret.min()
		return to_ret

	@staticmethod
	def log_scale_standardize(vec):
		vec_ss = (np.log(vec + 1) / np.log(2))
		vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
		vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
		return vec_ss

	@staticmethod
	def sqrt_scale_standardize(vec):
		vec_ss = np.sqrt(vec)
		vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
		vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
		return vec_ss

	@staticmethod
	def ecdf_scale_standardize(vec):
		vec_ss = ECDF(vec)(vec)
		vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
		return vec_ss

	@staticmethod
	def percentile(vec):
		vec_ss = rankdata(vec, method='average') * (1. / len(vec))
		vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
		return vec_ss

	@staticmethod
	def percentile_ordinal(vec):
		vec_ss = rankdata(vec, method='ordinal') * (1. / len(vec))
		vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
		return vec_ss

	@staticmethod
	def percentile_min(vec):
		vec_ss = rankdata(vec, method='min') * (1. / len(vec))
		vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
		return vec_ss


class RudderChart:
	def __init__(self,
	             term_doc_matrix,
	             minimum_term_frequency=3,
	             jitter=0,
	             seed=0):
		'''
		:param term_doc_matrix: TermDocMatrix
		:param jitter: float
		:param seed: float
		'''
		self.term_doc_matrix = term_doc_matrix
		self.jitter = jitter
		self.minimum_term_frequency = minimum_term_frequency
		self.seed = seed
		np.random.seed(seed)

	def add_jitter(self, vec):
		'''
		:param vec: array to jitter
		:return:
		'''
		if self.jitter == 0:
			return vec
		else:
			to_ret = vec + np.random.rand(1, len(vec))[0] * self.jitter
			return to_ret

	def draw(self,
	         category,
	         num_top_words_to_annotate=4,
	         words_to_annotate=[],
	         scores = None,
	         transform=percentile_min):

		font = {'family': 'sans-serif',
		        'color': 'black',
		        'weight': 'normal',
		        'size': 'large'
		        }
		df = self.term_doc_matrix.get_term_freq_df()
		df['category score'] = np.array(self.term_doc_matrix.get_rudder_scores(category))
		df['not category score'] = np.sqrt(2) - np.array(self.term_doc_matrix.get_rudder_scores(category))
		other_categories = [val + ' freq' for _, val \
		                    in self.term_doc_matrix._category_idx_store.items() \
		                    if val != category]
		all_categories = other_categories + [category + ' freq']
		df['color_scores'] = scores if scores is not None else np.array(self.term_doc_matrix.get_scaled_f_scores(category))

		df = filter_bigrams_by_pmis(
			df[df[all_categories].sum(axis=1) > self.minimum_term_frequency],
			threshold_coef=3)

		df['category score rank'] = rankdata(df['category score'], method='ordinal')
		df['not category score rank'] = rankdata(df['not category score'], method='ordinal')
		x_data_raw = transform(df[other_categories].sum(axis=1))
		y_data_raw = transform(df[category + ' freq'])
		x_data = self.add_jitter(x_data_raw)
		y_data = self.add_jitter(y_data_raw)
		df = df.reset_index()
		df_to_annotate = df[(df['not category score rank'] <= num_top_words_to_annotate)
		                    | (df['category score rank'] <= num_top_words_to_annotate)
		                    | df['term'].isin(words_to_annotate)]
		words = list(df['term'])

		fig, ax = plt.subplots()
		plt.figure(figsize=(10, 10))
		plt.gcf().subplots_adjust(bottom=0.2)
		plt.gcf().subplots_adjust(right=0.2)

		points = ax.scatter(x_data,
		                    y_data,
		                    c=-df['color_scores'],
		                    cmap='seismic',
		                    s=10,
		                    edgecolors='none',
		                    alpha=0.9)
		tooltip = plugins.PointHTMLTooltip(points,
		                                   ['<span id=a>%s</span>' % w for w in words],
		                                   css='#a {background-color: white;}')
		plugins.connect(fig, tooltip)
		ax.set_ylim([-.2, 1.2])
		ax.set_xlim([-.2, 1.2])
		ax.xaxis.set_ticks([0., 0.5, 1.])
		ax.yaxis.set_ticks([0., 0.5, 1.])
		ax.set_ylabel(category.title() + ' Frequency Percentile', fontdict=font, labelpad=20)
		ax.set_xlabel('Not ' + category.title() + ' Frequency Percentile', fontdict=font, labelpad=20)

		for i, row in df_to_annotate.iterrows():
			# alignment_criteria = row['category score rank'] < row['not category score rank']
			alignment_criteria = i % 2 == 0
			horizontalalignment = 'right' if alignment_criteria else 'left'
			verticalalignment = 'bottom' if alignment_criteria else 'top'
			term = row['term']
			ax.annotate(term,
			            (x_data[i], y_data[i]),
			            size=15,
			            horizontalalignment=horizontalalignment,
			            verticalalignment=verticalalignment,
			            )
		# texts.append(
		# ax.text(row['dem freq scaled'], row['rep freq scaled'], row['word'])
		# )
		# adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
		plt.show()
		return df, fig_to_html(fig)
