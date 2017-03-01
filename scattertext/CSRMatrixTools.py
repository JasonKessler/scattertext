import numpy as np
from scipy.sparse import csr_matrix


class CSRMatrixFactory:
	''' Factory class to create a csr_matrix.
	'''
	def __init__(self):
		self.rows = []
		self.cols = []
		self.data = []
		self._max_col = 0
		self._max_row = 0

	def __setitem__(self, row_col, datum):
		'''Insert a value into the matrix

		Parameters
		----------
		row_col : tuple
			Row and column indices
		datum : float or int
			Numeric value to insert into the matrix


		>>> mat_fact = CSRMatrixFactory()
		>>> mat_fact[3,1] = 1

		Returns
		-------
		Noone
		'''
		row, col = row_col
		self.rows.append(row)
		self.cols.append(col)
		self.data.append(datum)
		if row > self._max_row: self._max_row = row
		if col > self._max_col: self._max_col = col

	def set_last_col_idx(self, last_col_idx):
		'''
		Parameters
		----------
		param last_col_idx : int
			number of columns
		'''
		assert last_col_idx >= self._max_col
		self._max_col = last_col_idx

	def get_csr_matrix(self, dtype=np.int32):
		return csr_matrix((self.data, (self.rows, self.cols)),
		                  shape=(self._max_row + 1, self._max_col + 1),
		                  dtype=dtype)


def delete_columns(mat, columns_to_delete):
	'''
	>>> a = csr_matrix(np.array([[0, 1, 3, 0, 1, 0],
		                           [0, 0, 1, 0, 1, 1]])
	>>> delete_columns(a, [1,2]).todense()
	matrix([[0, 0, 1, 0],
          [0, 0, 1, 1]])

	Parameters
	----------
	mat : csr_matrix
	columns_to_delete : list[int]

	Returns
	-------
	csr_matrix that is stripped of columns indices columns_to_delete
	'''
	column_mask = np.ones(mat.shape[1], dtype=bool)
	column_mask[columns_to_delete] = 0
	return mat.tocsc()[:, column_mask].tocsr()
