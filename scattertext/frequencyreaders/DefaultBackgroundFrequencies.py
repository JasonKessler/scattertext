import pkgutil
from io import StringIO

import pandas as pd
from scipy.stats import rankdata


class BackgroundFrequencyDataFramePreparer(object):
    @staticmethod
    def prep_background_frequency(df):
        df['rank'] = rankdata(df.background, method='dense')
        df['background'] = df['rank'] / df['rank'].max()
        return df[['background']]


class BackgroundFrequenciesFromCorpus(BackgroundFrequencyDataFramePreparer):
    def __init__(self, corpus, exclude_categories=[]):
        self.background_df = (pd.DataFrame(corpus.remove_categories(exclude_categories)
                                           .get_term_freq_df().sum(axis=1))
                              .rename(columns={0: 'background'}))

    def get_background_frequency_df(self):
        return self.background_df

    def get_background_rank_df(self):
        return self.prep_background_frequency(self.get_background_frequency_df())


class BackgroundFrequencies(BackgroundFrequencyDataFramePreparer):
    @staticmethod
    def get_background_frequency_df(frequency_path=None):
        raise Exception

    @classmethod
    def get_background_rank_df(cls, frequency_path=None):
        return cls.prep_background_frequency(
            cls.get_background_frequency_df(frequency_path)
        )


class DefaultBackgroundFrequencies(BackgroundFrequencies):
    @staticmethod
    def get_background_frequency_df(frequency_path=None):
        if frequency_path:
            unigram_freq_table_buf = open(frequency_path)
        else:
            unigram_freq_table_buf = StringIO(pkgutil.get_data('scattertext', 'data/count_1w.txt')
                                              .decode('utf-8'))
        to_ret = (pd.read_csv(unigram_freq_table_buf,
                              sep='\t',
                              names=['word', 'background'])
                  .sort_values(ascending=False, by='background')
                  .drop_duplicates(['word'])
                  .set_index('word'))
        return to_ret
