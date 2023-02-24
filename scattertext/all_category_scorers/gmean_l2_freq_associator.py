import pandas as pd
import numpy as np
from scipy.stats import gmean
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression

from scattertext import Scalers
from scattertext.all_category_scorers.all_category_scorer import AllCategoryScorer

COEF_WEIGHT_DEFAULT = 2
FREQ_WEIGHT_DEFAULT = 1


class AllCategoryScorerGMeanL2(AllCategoryScorer):
    def _free_init(self, **kwargs):
        if 'coef_weight' in kwargs:
            assert int(kwargs['coef_weight']) == kwargs['coef_weight']
            assert kwargs['coef_weight'] > 1
            self.coef_weight_ = kwargs['coef_weight']
        else:
            self.coef_weight_ = COEF_WEIGHT_DEFAULT

        if 'freq_weight' in kwargs:
            assert int(kwargs['freq_weight']) == kwargs['freq_weight']
            assert kwargs['freq_weight'] > 1
            self.freq_weight_ = kwargs['freq_weight']
        else:
            self.freq_weight_ = FREQ_WEIGHT_DEFAULT

    def get_rank_freq_df(self) -> pd.DataFrame:
        coef_freq_df = self.__coefs_to_coef_freq_df(coef_df=self.__get_coef_df())
        coef_freq_df = self.__add_gmeans_to_coef_freq_df(coef_freq_df)
        data = []
        for cat in self.corpus_.get_categories():
            cat = str(cat)
            for term_rank, (term, row) in enumerate(
                    coef_freq_df[[cat + ' gmean', cat + ' freq']].sort_values(
                        by=cat + ' gmean',
                        ascending=False
                    ).iterrows()
            ):
                data.append({'Category': cat,
                             'Term': term,
                             'Rank': term_rank,
                             'Score': row[cat + ' gmean'],
                             'Frequency': row[cat + ' freq']})
        return pd.DataFrame(data)

    def __add_gmeans_to_coef_freq_df(self, coef_freq_df: pd.DataFrame) -> pd.DataFrame:
        for cat in self.corpus_.get_categories():
            freq = Scalers.dense_rank(coef_freq_df[str(cat) + ' freq'])
            coef = Scalers.scale_neg_1_to_1_with_zero_mean(coef_freq_df[str(cat) + ' coef'])
            coef_freq_df[str(cat) + ' gmean'] = gmean(([freq] * self.freq_weight_) + ([coef] * self.coef_weight_))
        return coef_freq_df

    def __coefs_to_coef_freq_df(self, coef_df: pd.DataFrame) -> pd.DataFrame:
        coef_freq_df = pd.merge(
            self.corpus_.get_freq_df(use_metadata=self.non_text_),
            coef_df,
            left_index=True,
            right_index=True
        )
        return coef_freq_df

    def __get_coef_df(self) -> pd.DataFrame:
        tdm = self.corpus_.get_term_doc_mat(non_text=self.non_text_)
        tdmtfidf = TfidfTransformer().fit_transform(tdm)
        coefs = np.zeros(shape=(self.corpus_.get_num_categories(), tdm.shape[1]), dtype=float)

        for i, cat in enumerate(self.corpus_.get_categories()):
            y = self.corpus_.get_category_ids() == i
            clf = LogisticRegression(
                penalty='l2', C=5., max_iter=4000, tol=1e-6, solver='liblinear'
            ).fit(tdmtfidf, y)
            coefs[i, :] = clf.coef_
        return pd.DataFrame(
            coefs.T,
            index=self.corpus_.get_terms(use_metadata=self.non_text_),
            columns=[str(x) + ' coef' for x in self.corpus_.get_categories()]
        )
