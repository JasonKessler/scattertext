from unittest import TestCase

from scattertext.indexstore.IndexStore import IndexStore


class TestIndexStore(TestCase):
	def test_main(self):
		index_store = IndexStore()
		self.assertEqual(index_store.getidx('a'), 0)
		self.assertEqual(index_store.getidx('b'), 1)
		self.assertEqual(index_store.getidx('a'), 0)
		self.assertEqual(index_store.getval(0), 'a')
		self.assertEqual(index_store.getval(1), 'b')
		self.assertTrue('a' in index_store)
		self.assertFalse('c' in index_store)
		self.assertEqual(set(index_store.values()), set(['a','b']))
		self.assertFalse(0 in index_store)
		self.assertTrue(index_store.hasidx(0))
		self.assertFalse(index_store.hasidx(2))
		self.assertEqual(index_store.getnumvals(), 2)
		self.assertEqual(list(index_store.items()), [(0, 'a'), (1, 'b')])

	def test_getidxstrict(self):
		index_store = IndexStore()
		self.assertEqual(index_store.getidx('a'), 0)
		self.assertEqual(index_store.getidx('b'), 1)
		self.assertEqual(index_store.getidx('a'), 0)
		with self.assertRaises(KeyError):
			index_store.getidxstrict('c')

	def test_batch_delete(self):
		index_store = IndexStore()
		self.assertEqual(index_store.getidx('a'), 0)
		self.assertEqual(index_store.getidx('b'), 1)
		self.assertEqual(index_store.getidx('c'), 2)
		self.assertEqual(index_store.getidx('d'), 3)
		with self.assertRaises(KeyError):
			new_idx_store = index_store.batch_delete_vals(['e', 'c'])
		new_idx_store = index_store.batch_delete_vals(['b','c'])
		self.assertEqual(new_idx_store.getidx('a'), 0)
		self.assertEqual(new_idx_store.getidx('c'), 2)
		self.assertEqual(new_idx_store.getidx('e'), 3)
		self.assertEqual(index_store.getidx('d'), 3)
		self.assertEqual(index_store.getidx('c'), 2)
		self.assertEqual(index_store.getidx('b'), 1)
		self.assertEqual(index_store.getidx('a'), 0)
		with self.assertRaises(ValueError):
			new_idx_store = index_store.batch_delete_idx([5, 1])
		new_idx_store = index_store.batch_delete_idx([2, 1])
		self.assertEqual(new_idx_store.getidx('a'), 0)
		self.assertEqual(new_idx_store.getidx('c'), 2)
		self.assertEqual(new_idx_store.getidx('e'), 3)


	def test_getidxstrictbatch(self):
		index_store = IndexStore()
		self.assertEqual(index_store.getidx('a'), 0)
		self.assertEqual(index_store.getidx('b'), 1)
		self.assertEqual(index_store.getidx('c'), 2)
		self.assertEqual(index_store.getidx('d'), 3)
		self.assertEqual(index_store.getidx('e'), 4)
		self.assertEqual(index_store.getidx('f'), 5)
		self.assertEqual(index_store.getidxstrictbatch(['b','f','b','a']), [1,5,1,0])

	def test_batch_delete_extra(self):
		index_store = IndexStore()
		self.assertEqual(index_store.getidx('a'), 0)
		self.assertEqual(index_store.getidx('b'), 1)
		self.assertEqual(index_store.getidx('c'), 2)
		self.assertEqual(index_store.getidx('d'), 3)
		self.assertEqual(index_store.getidx('e'), 4)
		self.assertEqual(index_store.getidx('f'), 5)
		del_idxstore = index_store.batch_delete_vals(['b', 'e'])
		self.assertEqual(list(del_idxstore.items()), [(0, 'a'), (1, 'c'), (2, 'd'), (3, 'f')])

		del_idxstore2 = del_idxstore.batch_delete_vals([])
		self.assertEqual(list(del_idxstore.items()), list(del_idxstore2.items()))
