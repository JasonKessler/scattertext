import numpy as np
import pandas as pd
from scipy.stats import rankdata


class RankDifference(object):
	def get_scores(self, a, b):
		to_ret = (rankdata(a, 'dense') / np.max(rankdata(a, 'dense'))
		          - rankdata(b, 'dense') / np.max(rankdata(b, 'dense')))

		if type(a) == pd.Series:
			return pd.Series(to_ret, index=a.index)
		return to_ret

	def get_name(self):
		return 'Rank Difference'

	def get_default_score(self):
		return 0
