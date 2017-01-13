import sys
from unittest import TestCase

from scattertext.viz.HTMLVisualizationAssembly import HTMLVisualizationAssembly
from scattertext.viz.VizDataAdapter import VizDataAdapter


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
		                 self.make_assembler().to_html(), )

	def test_raise_invalid_protocol_exception(self):
		with self.assertRaisesRegexp(BaseException,
		                             "Invalid protocol: ftp.  Protocol must be either http or https."):
			self.make_assembler().to_html(protocol='ftp')

	def test_height_width_default(self):
		assembler = self.make_assembler()
		self.assertEqual(assembler._call_build_visualization_in_javascript(),
		                 "buildViz(undefined,undefined,null,null,true,false,false);")

	def test_color(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, color='d3.interpolatePurples')
		                  ._call_build_visualization_in_javascript()),
		                 'buildViz(undefined,undefined,null,d3.interpolatePurples,true,false,false);')
	def test_full_doc(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, use_full_doc=True)
		                  ._call_build_visualization_in_javascript()),
		                 'buildViz(undefined,undefined,null,null,true,true,false);')


	def test_grey_zero_scores(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, grey_zero_scores=True)
		                  ._call_build_visualization_in_javascript()),
		                 'buildViz(undefined,undefined,null,null,true,false,true);')

	def test_height_width_nondefault(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, width_in_pixels=1000)
		                  ._call_build_visualization_in_javascript()),
		                 "buildViz(1000,undefined,null,null,true,false,false);")

		self.assertEqual((HTMLVisualizationAssembly(visualization_data, height_in_pixels=60)
		                  ._call_build_visualization_in_javascript()),
		                 "buildViz(undefined,60,null,null,true,false,false);")

		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000)
		                  ._call_build_visualization_in_javascript()),
		                 "buildViz(1000,60,null,null,true,false,false);")

	def test_max_snippets(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            max_snippets=None)
		                  ._call_build_visualization_in_javascript()),
		                 "buildViz(1000,60,null,null,true,false,false);")

		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            max_snippets=100)
		                  ._call_build_visualization_in_javascript()),
		                 "buildViz(1000,60,100,null,true,false,false);")

	def make_assembler(self):
		visualization_data = self.make_adapter()
		assembler = HTMLVisualizationAssembly(visualization_data)
		return assembler

	def make_adapter(self):
		words_dict = {"info": {"not_category_name": "Republican", "category_name": "Democratic"},
		              "data": [{"y": 0.33763837638376387, "term": "crises", "ncat25k": 0,
		                        "cat25k": 1, "x": 0.0, "s": 0.878755930416447},
		                       {"y": 0.5, "term": "something else", "ncat25k": 0,
		                        "cat25k": 1, "x": 0.0,
		                        "s": 0.5}]}
		visualization_data = VizDataAdapter(words_dict)
		return visualization_data
