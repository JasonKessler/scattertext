import numpy as np
from scipy.sparse import csr_matrix


class CSRMatrixFactory:
	def __init__(self):
		self.rows = []
		self.cols = []
		self.data = []
		self._max_col = 0
		self._max_row = 0

	def __setitem__(self, row_col, datum):
		'''
		:param row_col: (int, int)
		:param datum: int
		:return: None

		>>> mat_fact = CSRMatrixFactory()
		>>> mat_fact[3,1] = 1
		'''
		row, col = row_col
		self.rows.append(row)
		self.cols.append(col)
		self.data.append(datum)
		if row > self._max_row: self._max_row = row
		if col > self._max_col: self._max_col = col

	def get_csr_matrix(self):
		return csr_matrix((self.data, (self.rows, self.cols)),
		                  shape=(self._max_row + 1, self._max_col + 1),
		                  dtype=np.int32)