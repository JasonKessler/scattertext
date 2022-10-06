from typing import Any, Iterable, List, Set, Tuple


class IndexStore(object):
	def __init__(self):
		self._next_i = 0
		self._i2val = []
		self._val2i = {}

	def getval(self, idx: int) -> Any:
		return self._i2val[idx]

	def getvalbatch(self, y: Iterable) -> List[Any]:
		return [self._i2val[x] for x in y]

	def __len__(self) -> int:
		return len(self._i2val)

	def __contains__(self, val: Any) -> bool:
		return self._hasval(val)

	def _hasval(self, val: Any) -> bool:
		return val in self._val2i

	def getidxstrictbatch(self, vals: Iterable[Any]) -> List[int]:
		return [self._val2i[t] for t in vals]

	def getidx(self, val: Any) -> int:
		try:
			return self._val2i[val]
		except KeyError:
			self._val2i[val] = self._next_i
			self._i2val.append(val)
			self._next_i += 1
			return self._next_i - 1

	def getidxstrict(self, val: Any) -> int:
		return self._val2i[val]

	def getnumvals(self) -> int:
		return self._next_i

	def getvals(self) -> Set[Any]:
		return set(self._i2val)

	def hasidx(self, idx: int) -> bool:
		return 0 <= idx < self._next_i

	def items(self) -> Iterable[Tuple[int, Any]]:
		return enumerate(self._i2val)

	def batch_delete_vals(self, values: Iterable[any]) -> 'IndexStore':
		idx_delete_list = []
		for val in values:
			if not self._hasval(val):
				raise KeyError(str(val) + ' not found')
			idx_delete_list.append(self.getidx(val))
		return self.batch_delete_idx(idx_delete_list)

	def batch_delete_idx(self, idx_list: Iterable[int]) -> 'IndexStore':
		new_idxstore = IndexStore()
		last_idx_to_delete = -1
		number_of_values = self.getnumvals()
		for idx_to_delete in sorted(idx_list):
			if idx_to_delete >= number_of_values:
				raise ValueError('index ' + str(idx_to_delete) + ' not found')
			new_idxstore._i2val += self._i2val[last_idx_to_delete + 1:idx_to_delete]
			last_idx_to_delete = idx_to_delete
		new_idxstore._i2val += self._i2val[last_idx_to_delete + 1:]
		new_idxstore._val2i = {val: i for i, val in enumerate(new_idxstore._i2val)}
		new_idxstore._next_i = len(new_idxstore._val2i)

		return new_idxstore

	def _regenerate_val2i_and_next_i(self) -> None:
		self._val2i = {val: idx for idx, val in enumerate(self._i2val)}
		self._next_i = len(self._i2val)

	def values(self) -> List[Any]:
		'''

		Returns
		-------
		list
			A list containing all values registered.
		'''
		return self._i2val

