from unittest import TestCase

from scattertext.indexstore.IndexStoreFromList import IndexStoreFromList


class TestIndexStoreFromList(TestCase):
	def test_index_store_from_dict(self):
		values = ['a', 'b', 'c']
		idxstore = IndexStoreFromList.build(values)
		for idx, term in enumerate(values):
			self.assertEqual(idxstore.getidx(term), idx)
		self.assertEqual(idxstore._next_i, len(values))
