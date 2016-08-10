from unittest import TestCase

from scattertext.viz.HTMLVisualizationAssembly import HTMLVisualizationAssembly
from scattertext.viz.VizDataAdapter import VizDataAdapter
import sys

class TestHTMLVisualizationAssembly(TestCase):
	def test_main(self):
		words_dict = {"info": {"not_category_name": "Republican", "category_name": "Democratic"},
		              "data": [{"y": 0.33763837638376387, "term": "crises", "ncat25k": 0,
		                        "cat25k": 1, "x": 0.0, "s": 0.878755930416447},
		                       {"y": 0.5, "term": "something else", "ncat25k": 0, "cat25k": 1, "x": 0.0,
		                        "s": 0.5}]}
		visualization_data = VizDataAdapter(words_dict)
		assembler = HTMLVisualizationAssembly(visualization_data)
		html = assembler.to_html()
		if sys.version_info.major == 2:
			self.assertEqual(type(html), unicode)
		else:
			self.assertEqual(type(html), str)
		self.assertFalse('<!-- INSERT SCRIPT -->' in html)
		self.assertTrue('Republican' in html)




