from scattertext.indexstore import IndexStore


class IndexStoreFromDict(object):
	@staticmethod
	def build(term_to_index_dict):
		'''
		Parameters
		----------
		term_to_index_dict: term -> idx dictionary

		Returns
		-------
		IndexStore
		'''
		idxstore = IndexStore()
		idxstore._val2i = term_to_index_dict
		idxstore._next_i = len(term_to_index_dict)
		idxstore._i2val = [None for _ in range(idxstore._next_i)]
		for term, idx in idxstore._val2i.items():
			idxstore._i2val[idx] = term
		return idxstore