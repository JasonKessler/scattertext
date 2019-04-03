import numpy as np
import pandas as pd
from scipy.stats import rankdata


def scale(vec, terms=None, other_vec=None):
	return (vec - vec.min()) / (vec.max() - vec.min())


def scale_neg_1_to_1_with_zero_mean_abs_max(vec):
	max_abs = max(vec.max(), -vec.min())
	return ((((vec > 0).astype(float) * (vec / max_abs)) * 0.5 + 0.5)
	        + ((vec < 0).astype(float) * (vec / max_abs) * 0.5))

def scale_neg_1_to_1_with_zero_mean(vec):
	return ((((vec > 0).astype(float) * (vec / vec.max())) * 0.5 + 0.5)
	        + ((vec < 0).astype(float) * (vec / (-vec.min())) * 0.5))



def scale_neg_1_to_1_with_zero_mean_rank_abs_max(v):
	rankv = v * 2 - 1
	pos_v = rankv[rankv > 0]
	pos_v = rankdata(pos_v, 'dense')
	pos_v = pos_v / pos_v.max()
	neg_v = rankv[rankv < 0]
	neg_v = rankdata(neg_v, 'dense')
	neg_v = neg_v / neg_v.max()
	rankv[rankv > 0] = pos_v
	rankv[rankv < 0] = - (neg_v.max() - neg_v)

	return scale_neg_1_to_1_with_zero_mean_abs_max(rankv)


def scale_neg_1_to_1_with_zero_mean_log_abs_max(v):
	'''
	!!! not working
	'''
	df = pd.DataFrame({'v':v,
	                   'sign': (v > 0) * 2 - 1})
	df['lg'] = np.log(np.abs(v)) / np.log(1.96)
	df['exclude'] = (np.isinf(df.lg) | np.isneginf(df.lg))
	for mask in [(df['sign'] == -1) & (df['exclude'] == False),
	             (df['sign'] == 1) & (df['exclude'] == False)]:
		df[mask]['lg'] = df[mask]['lg'].max() - df[mask]['lg']
	df['lg'] *= df['sign']
	df['lg'] = df['lg'].fillna(0)
	print(df[df['exclude']]['lg'].values)
	#to_rescale = convention_df['lg'].reindex(v.index)
	df['to_out'] =  scale_neg_1_to_1_with_zero_mean_abs_max(df['lg'])
	print('right')
	print(df.sort_values(by='lg').iloc[:5])
	print(df.sort_values(by='lg').iloc[-5:])
	print('to_out')
	print(df.sort_values(by='to_out').iloc[:5])
	print(df.sort_values(by='to_out').iloc[-5:])
	print(len(df), len(df.dropna()))
	return df['to_out']


def scale_standardize(vec, terms=None, other_vec=None):
	to_ret = (vec - vec.mean()) / vec.std()
	to_ret += to_ret.min() + 1
	# to_ret = np.log(to_ret)/np.log(2)
	to_ret += to_ret.min()
	return to_ret


def log_scale_standardize(vec, terms=None, other_vec=None):
	vec_ss = (np.log(vec + 1) / np.log(2))
	vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
	return scale_0_to_1(vec_ss)


def sqrt_scale_standardize(vec, terms=None, other_vec=None):
	vec_ss = np.sqrt(vec)
	vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
	return scale_0_to_1(vec_ss)


def power_scale_standardize_factory(alpha):
	def f(vec, terms=None, other_vec=None):
		vec_ss = np.power(vec, 1. / alpha)
		vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
		return scale_0_to_1(vec_ss)

	return f


'''
from statsmodels.distributions import ECDF
def ecdf_scale_standardize(vec):
	vec_ss = ECDF(vec)(vec)
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss
'''


def power_scale_factory(alpha):
	def f(vec, terms=None, other_vec=None):
		return scale_0_to_1(np.power(vec, 1. / alpha))

	return f


def sqrt_scale(vec, terms=None, other_vec=None):
	return scale_0_to_1(np.sqrt(vec))


def log_scale(vec, terms=None, other_vec=None):
	return scale_0_to_1(np.log(vec))


def percentile(vec, terms=None, other_vec=None):
	vec_ss = rankdata(vec, method='average') * (1. / len(vec))
	return scale_0_to_1(vec_ss)


def dense_rank(vec, terms=None, other_vec=None):
	vec_ss = rankdata(vec, method='dense') * (1. / len(vec))
	return scale_0_to_1(vec_ss)
percentile_dense = dense_rank

def percentile_ordinal(vec, terms=None, other_vec=None):
	vec_ss = rankdata(vec, method='ordinal') * (1. / len(vec))
	return scale_0_to_1(vec_ss)


def percentile_min(vec, terms=None, other_vec=None):
	vec_ss = rankdata(vec, method='min') * (1. / len(vec))
	return scale_0_to_1(vec_ss)


def percentile_alphabetical(vec, terms, other_vec=None):
	scale_df = pd.DataFrame({'scores': vec, 'terms': terms})
	if other_vec is not None:
		scale_df['others'] = other_vec
	else:
		scale_df['others'] = 0
	vec_ss = (scale_df
		.sort_values(by=['scores', 'terms', 'others'],
	               ascending=[True, True, False])
		.reset_index()
		.sort_values(by='index')
		.index)
	return scale_0_to_1(vec_ss)

def stretch_0_to_1(vec):
	a = stretch_neg1_to_1(vec)
	return 0.5 * (a + 1)


def stretch_neg1_to_1(vec):
	a = np.copy(vec)
	if sum(a < 0):
		a[a < 0] = -a[a < 0] * 1. / a[a < 0].min()
	if sum(a > 0):
		a[a > 0] = a[a > 0] * 1. / a[a > 0].max()
	return a


def scale_0_to_1(vec_ss):
	vec_ss = (vec_ss - vec_ss.min()) * 1. / (vec_ss.max() - vec_ss.min())
	return vec_ss
