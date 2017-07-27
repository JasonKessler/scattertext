from unittest import TestCase

from scattertext.emojis.EmojiExtractor import extract_emoji


class TestExtract_emoji(TestCase):
	def test_extract_emoji(self):
		text_ords = [128589, 127998, 97, 102, 100, 115, 128077, 128077, 127998, 127873, 128175]
		text = ''.join([chr(c) for c in text_ords])
		result = [[ord(c) for c in pic] for pic in extract_emoji(text)]
		self.assertEqual(result,
		                 [[128589, 127998], [128077], [128077, 127998], [127873], [128175]])

	def test_extract_emoji_ensure_no_numbers(self):
		text_ords = [50, 49, 51, 52, 50, 51, 128587, 127995, 128587, 127995, 97, 32, 97, 106, 97, 107, 115, 100, 108, 32,
		             102, 97, 115, 108, 107, 51, 32, 107, 32, 51, 32, 35, 32, 94, 32, 64, 32, 33, 32, 32, 35, 32, 42, 32,
		             60, 32, 62, 32, 63, 32, 32, 34, 32, 46, 32, 44, 32, 32, 41, 32, 40, 32, 36]
		text = ''.join([chr(c) for c in text_ords])
		result = [[ord(c) for c in pic] for pic in extract_emoji(text)]
		self.assertEqual(result, [[128587, 127995], [128587, 127995]])
