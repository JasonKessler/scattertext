import pandas as pd

from scattertext import FeatsFromSpacyDoc

class FeatsFromScoredLexicon(FeatsFromSpacyDoc):
    def __init__(self,
                 lexicon_df,
                 use_lemmas=False,
                 **kwargs):
        '''
        Parameters
        ----------
        lexicon_df: pd.DataFrame, Indexed on terms, columns are scores for each category

        Other parameters from FeatsFromSpacyDoc.__init__

        Example:
        >>> print(lexicon_df)
                     activation  imagery  pleasantness
        word
        a                1.3846      1.0        2.0000
        abandon          2.3750      2.4        1.0000
        abandoned        2.1000      3.0        1.1429
        abandonment      2.0000      1.4        1.0000
        abated           1.3333      1.2        1.6667
        '''
        assert type(lexicon_df) == pd.DataFrame
        self._lexicon_df = lexicon_df
        super(FeatsFromScoredLexicon, self).__init__(use_lemmas, **kwargs)

    def get_doc_metadata(self, doc, prefix=''):
        '''

        :param doc: spacy.Doc
        :param prefix: str, default is ''
        :return: pd.Series
        '''
        out_series = pd.merge(
            pd.DataFrame(pd.Series([tok.lemma_ if self._use_lemmas else tok.lower_
                                    for tok in doc]).value_counts(), columns=['count']),
            self._lexicon_df, left_index=True, right_index=True
        ).drop(columns=['count']).mean(axis=0)
        if prefix == '':
            return out_series
        return pd.Series(out_series.values, index=[prefix + x for x in out_series.index])

    def has_metadata_term_list(self):
        return True

    def get_top_model_term_lists(self):
        return {col: list(self._lexicon_df[col].sort_values(ascending=False).iloc[:10].index)
                for col in self._lexicon_df}
