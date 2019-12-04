# Helper functions for loading lexicons
import io
import pkgutil

import pandas as pd
import numpy as np


class WhissellsLexicon(object):
    '''
    From http://www.cs.columbia.edu/~julia/papers/dict_of_affect/DictionaryofAffect.

    Developed by Cynthia Whissell at Laurentian University.

    Header:
    new dictionary with imagery (c) C Whissell


    comment w=word, ee=pleasantness, aa=activation, ii=imagery

    comment scores for pleasantness range from 1 (unpleasant) to 3 (pleasant)
            scores for activation range from 1 (passive) to 3 (active)
            scores for imagery range from 1 (difficult to form a meantal
              picture of this word) to 3 (easy to form a mental picture)

    comment pleasantness mean=1.84, sd=.44
            activation mean=1.85, sd=.39
            imagery (does word give you a clear mental picture) mean=1.94, sd=.63

    comment these values have been tested on 348,000 words of natural language
        the dictionary has a 90% matching rate for this corpus
        mean ee is 1.85, with an sd of .36
        mean aa is 1.67, with an sd of .36
        mean ii is 1.52, with an sd of .63

    '''

    @staticmethod
    def get_data():
        '''
        Returns
        -------
        pd.DataFrame

        I.e.,
        >>> print(WhissellsLexicon.get_data())
                     activation  imagery  pleasantness
        word
        a                1.3846      1.0        2.0000
        abandon          2.3750      2.4        1.0000
        abandoned        2.1000      3.0        1.1429
        abandonment      2.0000      1.4        1.0000
        abated           1.3333      1.2        1.6667
        '''
        data_stream = pkgutil.get_data('scattertext', 'data/whissells_df.csv')
        return pd.read_csv(
            io.StringIO(data_stream.decode('utf8'))
        ).set_index('word').astype(np.float64)
