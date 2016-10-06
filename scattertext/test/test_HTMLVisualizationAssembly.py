from unittest import TestCase

from scattertext.viz.HTMLVisualizationAssembly import HTMLVisualizationAssembly, InvalidProtocolException
from scattertext.viz.VizDataAdapter import VizDataAdapter
import sys

class TestHTMLVisualizationAssembly(TestCase):
	def test_main(self):
		assembler = self.make_assembler()
		html = assembler.to_html()
		if sys.version_info.major == 2:
			self.assertEqual(type(html), unicode)
		else:
			self.assertEqual(type(html), str)
		self.assertFalse('<!-- INSERT SCRIPT -->' in html)
		self.assertTrue('Republican' in html)

	def test_protocol_is_https(self):
		html = self.make_assembler().to_html(protocol='https')
		self.assertTrue('https://' in html)
		self.assertFalse('http://' in html)

	def test_protocol_is_http(self):
		html = self.make_assembler().to_html(protocol='http')
		self.assertFalse('https://' in html)
		self.assertTrue('http://' in html)

	def test_protocol_defaults_to_http(self):
		self.assertEqual(self.make_assembler().to_html(protocol='http'),
		                 self.make_assembler().to_html(),)

	def test_raise_invalid_protocol_exception(self):
		with self.assertRaisesRegexp(InvalidProtocolException,
		                             "Invalid protocol: 'ftp'.  Protocol must be either http or https."):
			self.make_assembler().to_html(protocol='ftp')

	def make_assembler(self):
		words_dict = {"info": {"not_category_name": "Republican", "category_name": "Democratic"},
		              "data": [{"y": 0.33763837638376387, "term": "crises", "ncat25k": 0,
		                        "cat25k": 1, "x": 0.0, "s": 0.878755930416447},
		                       {"y": 0.5, "term": "something else", "ncat25k": 0, "cat25k": 1, "x": 0.0,
		                        "s": 0.5}]}
		visualization_data = VizDataAdapter(words_dict)
		assembler = HTMLVisualizationAssembly(visualization_data)
		return assembler




