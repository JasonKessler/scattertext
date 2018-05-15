import pkgutil
from io import StringIO

import pandas as pd
from scipy.stats import rankdata


class BackgroundFrequencies(object):
	@staticmethod
	def get_background_frequency_df(frequency_path=None):
		raise Exception

	@classmethod
	def get_background_rank_df(cls, frequency_path=None):
		df = cls.get_background_frequency_df(frequency_path)
		df['rank'] = rankdata(df.background, method='dense')
		df['background'] = df['rank'] / df['rank'].max()
		return df[['background']]


class DefaultBackgroundFrequencies(BackgroundFrequencies):
	@staticmethod
	def get_background_frequency_df(frequency_path=None):
		if frequency_path:
			unigram_freq_table_buf = open(frequency_path)
		else:
			unigram_freq_table_buf = StringIO(pkgutil.get_data('scattertext', 'data/count_1w.txt')
			                                  .decode('utf-8'))
		to_ret = (pd.read_table(unigram_freq_table_buf,
		                        names=['word', 'background'])
		          .sort_values(ascending=False, by='background')
		          .drop_duplicates(['word'])
		          .set_index('word'))
		return to_ret
