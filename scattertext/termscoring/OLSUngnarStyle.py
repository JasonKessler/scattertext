import numpy as np
from scipy.sparse.linalg import lsqr


class OLSUngarStyle(object):
	def get_scores_and_p_values(self, tdm, category):
		'''
		Parameters
		----------
		tdm: TermDocMatrix
		category: str, category name

		Returns
		-------
		pd.DataFrame(['coef', 'p-val'])
		'''
		X = tdm._X
		y = self._make_response_variable_1_or_negative_1(category, tdm)
		pX = X / X.sum(axis=1)
		ansX = self._anscombe_transform(pX.copy())
		B, istop, itn, r1norm, r2norm, anorm, acond, arnorm, xnorm, var\
			= lsqr(A=ansX, b=y, calc_var=True)


	def _make_response_variable_1_or_negative_1(self, category, tdm):
		'''
		Parameters
		----------
		category, str
		tdm, TermDocMatrix

		Returns
		-------
		np.array
		'''
		return (tdm.get_category_names_by_row() == category).astype(int) * 2 - 1

	def _anscombe_transform(self, X):
		'''
		Parameters
		----------
		ansX

		Returns
		-------
		csr_matrix
		'''
		return 2 * np.sqrt(np.array(X) + 3. / 8)
