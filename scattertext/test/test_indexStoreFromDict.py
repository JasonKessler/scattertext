from unittest import TestCase

from scattertext.indexstore.IndexStoreFromDict import IndexStoreFromDict


class TestIndexStoreFromDict(TestCase):
	def test_index_store_from_dict(self):
		vocab = {'baloney': 0,
		         'by': 1,
		         'first': 2,
		         'has': 3,
		         'it': 4,
		         'meyer': 5,
		         'my': 6,
		         'name': 7,
		         'oscar': 8,
		         'second': 9}

		idxstore = IndexStoreFromDict.build(vocab)
		for term, idx in vocab.items():
			self.assertEqual(idxstore.getidx(term), idx)
		self.assertEqual(idxstore.getnumvals(), len(vocab))