from unittest import TestCase

from scattertext.Formatter import large_int_format


class TestLarge_int_format(TestCase):
	def test_large_int_format(self):
		self.assertEqual(large_int_format(1), '1')
		self.assertEqual(large_int_format(6), '6')
		self.assertEqual(large_int_format(10), '10')
		self.assertEqual(large_int_format(19), '10')
		self.assertEqual(large_int_format(88), '80')
		self.assertEqual(large_int_format(999), '900')
		self.assertEqual(large_int_format(1001), '1k')
		self.assertEqual(large_int_format(205001), '200k')
		self.assertEqual(large_int_format(2050010), '2mm')
		self.assertEqual(large_int_format(205000010), '200mm')
		self.assertEqual(large_int_format(2050000010), '2b')
