class IndexStore:
	def __init__(self):
		self._next_i = 0
		self._i2val = []
		self._val2i = {}

	def getval(self, idx):
		return self._i2val[idx]

	def __contains__(self, val):
		return self._hasval(val)

	def _hasval(self, val):
		return val in self._val2i

	def getidx(self, val):
		try:
			return self._val2i[val]
		except KeyError:
			self._val2i[val] = self._next_i
			self._i2val.append(val)
			self._next_i += 1
			return self._next_i - 1

	def getnumvals(self):
		return self._next_i

	def getvals(self):
		return set(self._i2val)

	def hasidx(self, idx):
		return 0 <= idx < self._next_i

	def items(self):
		return enumerate(self._i2val)
