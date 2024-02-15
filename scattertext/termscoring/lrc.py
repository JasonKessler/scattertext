from typing import Union

import numpy as np
import pandas as pd
from scipy.stats import beta

from scattertext import CorpusBasedTermScorer

"""
Note that the functions here are more or less a direct translation from the LRC implementation in R by Evert (2023).

Stephanie Evert. 2023. Measuring Keyness. https://osf.io/x8z9n.
"""


class LRC(CorpusBasedTermScorer):
    """
    LRC from Evert (2023).

    A direct translation of the R function from (Evert 2023)
    Stephanie Evert. 2023. Measuring Keyness. https://osf.io/x8z9n.
    """

    def _set_scorer_args(self, **kwargs):
        self.conf_level_ = kwargs.get('conf_level', 0.95)
        self.correct_ = kwargs.get('correct', True)
        self.alternative_ = kwargs.get('alternative', 'two sided')

    def _get_ns_and_fs(self, args):
        cat_X, ncat_X = self._get_cat_and_ncat(self._get_X())
        n1 = self._get_cat_size()
        n2 = self._get_ncat_size()
        if len(args) == 0:
            f1 = cat_X.sum(axis=0).A1
            f2 = ncat_X.sum(axis=0).A1
        else:
            f1, f2 = self.__get_f1_f2_from_args(args)
        f1 = np.array(f1).astype(np.float64)
        f2 = np.array(f2).astype(np.float64)
        return n1, n2, f1, f2

    def get_scores(self, *args) -> pd.Series:
        n1, n2, f1, f2 = self._get_ns_and_fs(args)

        scores = lrc(f1=f1,
                     f2=f2,
                     n1=n1,
                     n2=n2,
                     conf_level=self.conf_level_,
                     correct=self.correct_,
                     alternative=self.alternative_)

        return pd.Series(scores, index=self._get_terms())

    def get_score_df(self, *args) -> pd.DataFrame:
        n1, n2, f1, f2 = self._get_ns_and_fs(args)

        return lrc_df(f1=f1,
                      f2=f2,
                      n1=n1,
                      n2=n2,
                      conf_level=self.conf_level_,
                      correct=self.correct_,
                      alternative=self.alternative_)

    def get_name(self):
        return 'LRC'


def lrc(f1: np.array,
        f2: np.array,
        n1: Union[int, np.array],
        n2: Union[int, np.array],
        conf_level: float = 0.95,
        correct: bool = True,
        alternative: str = 'two sided') -> np.array:
    return lrc_df(f1=f1,
                  f2=f2,
                  n1=n1,
                  n2=n2,
                  conf_level=conf_level,
                  correct=correct,
                  alternative=alternative).Score.values


def lrc_df(f1: np.array,
           f2: np.array,
           n1: Union[int, np.array],
           n2: Union[int, np.array],
           conf_level: float = 0.95,
           correct: bool = True,
           alternative: str = 'two sided') -> np.array:
    assert len(f1) == len(f2)
    assert np.all(f1 + f2 >= 1)
    score_df = lrc_score_df(f1=f1,
                            f2=f2,
                            n1=n1,
                            n2=n2,
                            conf_level=conf_level,
                            correct=correct,
                            alternative=alternative)
    return score_df


def lrc_score_df(f1: np.array,
                 f2: np.array,
                 n1: Union[int, np.array],
                 n2: Union[int, np.array],
                 conf_level: float = 0.95,
                 correct: bool = True,
                 alternative: str = 'two sided') -> pd.DataFrame:
    return binom_confint(
        k=f1,
        n=f1 + f2,
        conf_level=conf_level,
        correct=correct,
        alternative=alternative
    ).assign(
        P1=f1 / n1,
        P2=f2 / n2,
        Score=lambda df: np.where(
            df.P1 > df.P2,
            np.maximum(np.log2((n2 / n1) * df.lower / (1 - df.lower)), np.zeros(len(df))),
            np.minimum(np.log2((n2 / n1) * df.upper / (1 - df.upper)), np.zeros(len(df)))
        )
    )


def pmax(a, b):
    assert type(a) in [list, np.array]
    return pd.DataFrame({'A': a}).assign(B=b).max(axis=1).values


def pmin(a, b):
    assert type(a) in [list, np.array]
    return pd.DataFrame({'A': a}).assign(B=b).min(axis=1).values


def safe_qbeta(p, shape1, shape2, lower_tail=True):
    assert len(p) == len(shape1) and len(p) == len(shape2)
    is_0 = shape1 <= 0
    is_1 = shape2 <= 0
    ok = ~(is_0 | is_1)
    x = np.zeros(len(p))
    x[ok] = qbeta(p[ok], shape1[ok], shape2[ok], lower_tail=lower_tail)
    x[is_0 & ~is_1] = 0  # density concentrated at x = 0 (for alpha == 0)
    x[is_1 & ~is_0] = 1  # density concentrated at x = 1 (for beta == 0)
    x[is_0 & is_1] = np.nan  # shouldn't happen in our case (alpha == beta == 0)
    return x


def qbeta(p, shape1, shape2, lower_tail=True):
    if lower_tail is False:
        p = 1 - p
    return beta.ppf(q=p, a=shape1, b=shape2, loc=0, scale=1)


def binom_confint(k, n, conf_level=0.95, correct=True, alternative='two sided'):
    assert alternative in ("two sided", "less", "greater")
    assert np.all(k >= 0) and np.all(k <= n) and np.all(n >= 1)
    assert np.all(conf_level >= 0) and np.all(conf_level <= 1)

    alpha = (1 - conf_level) / 2 if (alternative == "two sided") else (1 - conf_level)
    if correct:
        alpha = alpha / len(k)
    alpha = np.array([alpha] * len(k))

    lower = safe_qbeta(alpha, k, n - k + 1)
    upper = safe_qbeta(alpha, k + 1, n - k, lower_tail=False)
    return pd.DataFrame({
        'lower': lower if alternative in ['two sided', 'greater'] else [0] * len(k),
        'upper': upper if alternative in ['two sided', 'less'] else [0] * len(k)
    })
