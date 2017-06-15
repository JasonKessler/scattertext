import sys
from unittest import TestCase

from scattertext.viz.HTMLVisualizationAssembly import HTMLVisualizationAssembly, DEFAULT_D3_URL, \
	DEFAULT_D3_SCALE_CHROMATIC
from scattertext.viz.VizDataAdapter import VizDataAdapter


class TestHTMLVisualizationAssembly(TestCase):
	def get_params(self, param_dict={}):
		params = ['undefined', 'undefined', 'null', 'null', 'true', 'false',
		          'false', 'false', 'false', 'true', 'false', 'false', 'true', '0.05',
		          'false', 'undefined', 'undefined']
		for i, val in param_dict.items():
			params[i] = val
		return 'buildViz(' + ','.join(params) + ');'

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

	def test_main(self):
		assembler = self.make_assembler()
		html = assembler.to_html()
		if sys.version_info.major == 2:
			self.assertEqual(type(html), unicode)
		else:
			self.assertEqual(type(html), str)
		self.assertFalse('<!-- EXTRA LIBS -->' in html)
		self.assertFalse('<!-- INSERT SCRIPT -->' in html)
		self.assertTrue('Republican' in html)

	def test_save_svg_button(self):
		assembly = HTMLVisualizationAssembly(self.make_adapter(), save_svg_button=True)
		html = assembly.to_html()
		self.assertEqual(assembly._call_build_visualization_in_javascript(),
		                 self.get_params({11: 'true'}))
		self.assertFalse('<!-- INSERT SCRIPT -->' in html)

	# self.assertTrue('d3-save-svg.min.js' in html)


	def test_protocol_is_https(self):
		html = self.make_assembler().to_html(protocol='https')
		self.assertTrue('https://' in html)
		self.assertFalse('http://' in html)

	def test_protocol_is_http(self):
		html = self.make_assembler().to_html(protocol='http')
		self.assertFalse('https://' in html)
		self.assertTrue('http://' in html)

	def test_protocol_default_d3_url(self):
		html = self.make_assembler().to_html()
		self.assertTrue(DEFAULT_D3_URL in html)
		html = self.make_assembler().to_html(d3_url='d3.js')
		self.assertTrue(DEFAULT_D3_URL not in html)
		self.assertTrue('d3.js' in html)

	def test_protocol_default_d3_chromatic_url(self):
		html = self.make_assembler().to_html()
		self.assertTrue(DEFAULT_D3_SCALE_CHROMATIC in html)
		html = self.make_assembler().to_html(d3_scale_chromatic_url='d3-scale-chromatic.v1.min.js')
		self.assertTrue(DEFAULT_D3_SCALE_CHROMATIC not in html)
		self.assertTrue('d3-scale-chromatic.v1.min.js' in html)

	def test_protocol_defaults_to_http(self):
		self.assertEqual(self.make_assembler().to_html(protocol='http'),
		                 self.make_assembler().to_html())

	def test_raise_invalid_protocol_exception(self):
		with self.assertRaisesRegexp(BaseException,
		                             "Invalid protocol: ftp.  Protocol must be either http or https."):
			self.make_assembler().to_html(protocol='ftp')

	def test_height_width_default(self):
		assembler = self.make_assembler()
		self.assertEqual(assembler._call_build_visualization_in_javascript(), self.get_params())

	def test_color(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, color='d3.interpolatePurples')
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({3: 'd3.interpolatePurples'}))

	def test_full_doc(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, use_full_doc=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({5: 'true'}))

	def test_grey_zero_scores(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, grey_zero_scores=True)
		                  ._call_build_visualization_in_javascript()), self.get_params({6: 'true'}))

	def test_chinese_mode(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, asian_mode=True)
		                  ._call_build_visualization_in_javascript()), self.get_params({7: 'true'}))

	def test_reverse_sort_scores_for_not_category(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, reverse_sort_scores_for_not_category=False)
		                  ._call_build_visualization_in_javascript()), self.get_params({12: 'false'}))

	def test_height_width_nondefault(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, width_in_pixels=1000)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000'}))

		self.assertEqual((HTMLVisualizationAssembly(visualization_data, height_in_pixels=60)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({1: '60'}))

		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60'}))

	def test_use_non_text_features(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            use_non_text_features=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 8: 'true'}))

	def test_show_characteristic(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            show_characteristic=False)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 9: 'false'}))

	def test_max_snippets(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            max_snippets=None)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60'}))

		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            max_snippets=100)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 2: '100'}))

	def test_word_vec_use_p_vals(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            word_vec_use_p_vals=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 10: 'true'}))

	def test_max_p_val(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            word_vec_use_p_vals=True,
		                                            max_p_val=0.01)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 10: 'true', 13: '0.01'}))

	def test_p_value_colors(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            word_vec_use_p_vals=True,
		                                            p_value_colors=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 10: 'true', 14: 'true'}))

	def test_x_label(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            x_label='x label')
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 15: '"x label"'}))

	def test_y_label(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            height_in_pixels=60,
		                                            width_in_pixels=1000,
		                                            y_label='y label')
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({0: '1000', 1: '60', 16: '"y label"'}))
