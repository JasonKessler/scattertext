from unittest import TestCase

import numpy as np

from scattertext.termsignificance import LogOddsRatioUninformativeDirichletPrior
from scattertext.termsignificance.LogOddsRatioUninformativeDirichletPrior import z_to_p_val
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_term_doc_mat


class TestLogOddsRatioUninformativeDirichletPrior(TestCase):
	def test_get_p_vals(self):
		tdm = build_hamlet_jz_term_doc_mat()
		df = tdm.get_term_freq_df()
		X = df[['hamlet freq', 'jay-z/r. kelly freq']].values
		pvals = LogOddsRatioUninformativeDirichletPrior().get_p_vals(X)
		self.assertGreaterEqual(min(pvals), 0)
		self.assertLessEqual(min(pvals), 1)

	def test_z_to_p_val(self):
		np.testing.assert_almost_equal(z_to_p_val(0), 0.5)
		np.testing.assert_almost_equal(z_to_p_val(1.96), 0.97500210485177952)
		np.testing.assert_almost_equal(z_to_p_val(-1.96), 0.024997895148220428)
		self.assertLessEqual(z_to_p_val(-0.1), z_to_p_val(0))
		self.assertLessEqual(z_to_p_val(0), z_to_p_val(0.1))
		self.assertLessEqual(z_to_p_val(0.1), z_to_p_val(0.2))