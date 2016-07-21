from unittest import TestCase

import numpy as np
from scipy.sparse import csr_matrix

from texttoideas import CSRMatrixFactory


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
