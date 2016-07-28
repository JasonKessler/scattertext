from unittest import TestCase

import numpy as np
from scipy.sparse import csr_matrix

import scattertext
from scattertext.CSRMatrixTools import CSRMatrixFactory


class TestCSRMatrixFactory(TestCase):
	def test_main(self):
		mat_factory = CSRMatrixFactory()
		mat_factory[0, 0] = 4
		mat_factory[1, 5] = 3
		mat = mat_factory.get_csr_matrix()
		self.assertEqual(type(mat), csr_matrix)
		np.testing.assert_array_almost_equal(
			np.array([[4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3]]),
			mat.todense())

	def test_delete_row(self):
		a = csr_matrix(np.array([[0, 1, 3, 0, 1, 0],
		                         [0, 0, 1, 0, 1, 1],
		                         [0, 5, 1, 0, 5, 5]]))
		b = scattertext.CSRMatrixTools.delete_columns(a, [0, 3])
		desired_array = np.array([[1, 3, 1, 0],
		                          [0, 1, 1, 1],
		                          [5, 1, 5, 5]])
		self.assertEqual(type(b), csr_matrix)
		np.testing.assert_array_almost_equal(b.todense(), desired_array)
		self.assertEqual(a.shape, (3,6))