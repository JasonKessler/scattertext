import numpy as np
import pandas as pd
from scipy.stats import chi2
from statsmodels.stats.multitest import fdrcorrection

from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer


def g2_term(O, E):
    res = O.astype(np.float64) * (np.log(O) - np.log(E))
    res[O == 0] = 0
    return res


def sign(a: np.array) -> np.array:
    return np.nan_to_num(a / np.abs(a), 0)


def qchisq(alpha: np.array, df: int) -> np.array:
    return chi2.ppf(1 - alpha, df=df)  # qchisq(alpha, df=1, lower.tail=FALSE)


class G2(CorpusBasedTermScorer):
    """
    G^2 (log likelihood ratio)s from (Rayson and Garside 2000)

    A direct translation of the R function from (Evert 2023)
    Stephanie Evert. 2023. Measuring Keyness. https://osf.io/x8z9n.
    G2.term <- function (O, E) {
      res <- O * log(O / E)
      res[O == 0] <- 0
      res
    }

    G2 <- function (f1, f2, N1, N2, alpha=NULL, correct=TRUE) {
      stopifnot(length(f1) == length(f2))

      ## observed and expected contingency tables
      N <- N1 + N2
      R1 <- f1 + f2
      O11 <- f1;      E11 <- R1 * N1 / N
      O12 <- f2;      E12 <- R1 * N2 / N
      O21 <- N1 - f1; E21 <- N1 - E11
      O22 <- N2 - f2; E22 <- N2 - E12

      ## log-likelihood statistic (simplest formula)
      G2 <- 2 * (G2.term(O11, E11) + G2.term(O12, E12) + G2.term(O21, E21) + G2.term(O22, E22))
      res <- sign(O11 - E11) * G2 # set sign to distinguish positive vs. negative keywords

      ## weed out non-significant items if alpha is specified
      if (!is.null(alpha)) {
        if (correct) alpha <- alpha / length(f1)
        theta <- qchisq(alpha, df=1, lower.tail=FALSE)
        res[G2 < theta] <- 0 # set to 0 if not significant at level alpha
      }

      res
    }
    """

    def _set_scorer_args(self, **kwargs):
        self.alpha_ = kwargs.get('alpha', None)
        self.correct_ = kwargs.get('correct', True)

    def get_score_df(self, label_append=''):
        N1, N2, f1, f2 = self._get_ns_and_fs(())
        gsquare, res = self._get_g2_and_res(N1, N2, f1, f2)
        df = pd.DataFrame({
            'G2': gsquare,
            'Score': res,
            'P': chi2.sf(gsquare, df=1),
        })
        return df.assign(
            CorrectedP = lambda df: fdrcorrection(pvals=df.P.values, alpha=self.alpha_, method='indep')[1]
        )



    def get_scores(self, *args) -> pd.Series:
        N1, N2, f1, f2 = self._get_ns_and_fs(args)

        gsquare, res = self._get_g2_and_res(N1, N2, f1, f2)

        ## weed out non-significant items if alpha is specified
        if self.alpha_ is not None:
            alpha = self.alpha_
            if self.correct_:
                alpha = alpha / len(f1)
            theta = qchisq(alpha, df=1)
            res[gsquare < theta] = 0  # set to 0 if not significant at level alpha

        return pd.Series(res, index=self._get_terms())

    def _get_g2_and_res(self, N1, N2, f1, f2):
        N = N1 + N2
        R1 = f1 + f2
        E11, E12, E21, E22, O11, O12, O21, O22 = self.__get_contingency_table(N, N1, N2, R1, f1, f2)
        ## log-likelihood statistic (simplest formula)
        gsquare = 2 * (g2_term(O11, E11) + g2_term(O12, E12) + g2_term(O21, E21) + g2_term(O22, E22))
        res = sign(O11 - E11) * gsquare  # set sign to distinguish positive vs. negative keywords
        return gsquare, res

    def __get_contingency_table(self, N, N1, N2, R1, f1, f2):
        O11 = f1
        E11 = R1 * N1 / N
        O12 = f2
        E12 = R1 * N2 / N
        O21 = N1 - f1
        E21 = N1 - E11
        O22 = N2 - f2
        E22 = N2 - E12
        return E11, E12, E21, E22, O11, O12, O21, O22

    def _get_ns_and_fs(self, args):
        cat_X, ncat_X = self._get_cat_and_ncat(self._get_X())
        N1 = self._get_cat_size()
        N2 = self._get_ncat_size()
        if len(args) == 0:
            f1 = cat_X.sum(axis=0).A1
            f2 = ncat_X.sum(axis=0).A1
        else:
            f1, f2 = self.__get_f1_f2_from_args(args)
        f1 = np.array(f1).astype(np.float64)
        f2 = np.array(f2).astype(np.float64)
        return N1, N2, f1, f2

    def get_name(self):
        return 'G2'
