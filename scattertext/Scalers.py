import numpy as np
from scipy.stats import rankdata


def scale(vec):
	return (vec - vec.min()) / (vec.max() - vec.min())


def scale_standardize(vec):
	to_ret = (vec - vec.mean()) / vec.std()
	to_ret += to_ret.min() + 1
	# to_ret = np.log(to_ret)/np.log(2)
	to_ret += to_ret.min()
	return to_ret


def log_scale_standardize(vec):
	vec_ss = (np.log(vec + 1) / np.log(2))
	vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss


def sqrt_scale_standardize(vec):
	vec_ss = np.sqrt(vec)
	vec_ss = (vec_ss - vec_ss.mean()) / vec_ss.std()
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss

'''
from statsmodels.distributions import ECDF
def ecdf_scale_standardize(vec):
	vec_ss = ECDF(vec)(vec)
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss
'''

def percentile(vec):
	vec_ss = rankdata(vec, method='average') * (1. / len(vec))
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss


def percentile_ordinal(vec):
	vec_ss = rankdata(vec, method='ordinal') * (1. / len(vec))
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss


def percentile_min(vec):
	vec_ss = rankdata(vec, method='min') * (1. / len(vec))
	vec_ss = (vec_ss - vec_ss.min()) / (vec_ss.max() - vec_ss.min())
	return vec_ss