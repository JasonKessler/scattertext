from scattertext.indexstore.IndexStore import IndexStore


class IndexStoreFromList(object):
	@staticmethod
	def build(values):
		'''
		Parameters
		----------
		values: [term, ...]

		Returns
		-------
		IndexStore
		'''
		idxstore = IndexStore()
		idxstore._i2val = list(values)
		idxstore._val2i = {term:i for i,term in enumerate(values)}
		idxstore._next_i = len(values)
		return idxstore