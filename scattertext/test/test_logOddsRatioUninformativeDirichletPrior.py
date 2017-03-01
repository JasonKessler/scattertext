from unittest import TestCase

from scattertext.termsignificance import LogOddsRatioUninformativeDirichletPrior
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_term_doc_mat


class TestLogOddsRatioUninformativeDirichletPrior(TestCase):
	def test_get_p_vals(self):
		tdm = build_hamlet_jz_term_doc_mat()
		df = tdm.get_term_freq_df()
		X = df[['hamlet freq', 'jay-z/r. kelly freq']].values
		pvals = LogOddsRatioUninformativeDirichletPrior().get_p_vals(X)
		self.assertGreaterEqual(min(pvals), 0)
		self.assertLessEqual(min(pvals), 1)

