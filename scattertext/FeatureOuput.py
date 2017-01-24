import numpy as np


class FeatureLister(object):
	def __init__(self, X, idx_store, num_docs):
		self.X = X
		self.idx_store = idx_store
		self.num_docs = num_docs

	def output(self):
		# () -> list
		toret = [{} for i in range(self.num_docs)]
		X = self.X.tocoo()
		for row, col, val in zip(X.row, X.col, X.data):
			toret[row][self.idx_store.getval(col)] = np.asscalar(val)
		return toret
