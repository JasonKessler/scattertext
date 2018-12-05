import sys
from unittest import TestCase

from scattertext import HTMLSemioticSquareViz
from scattertext.Common import DEFAULT_D3_URL, DEFAULT_D3_SCALE_CHROMATIC
from scattertext.test.test_semioticSquare import get_test_semiotic_square
from scattertext.viz.HTMLVisualizationAssembly import HTMLVisualizationAssembly
from scattertext.viz.VizDataAdapter import VizDataAdapter


class TestHTMLVisualizationAssembly(TestCase):
	def get_params(self, param_dict={}):
		params = ['1000', '600', 'null', 'null', 'true', 'false',
		          'false', 'false', 'false', 'true', 'false', 'false', 'true', '0.1',
		          'false', 'undefined', 'undefined', 'getDataAndInfo()', 'true', 'false',
		          'null', 'null', 'null', 'null', 'true', 'false', 'true', 'false',
		          'null', 'null', '10', 'null', 'null', 'null']
		for i, val in param_dict.items():
			params[i] = val
		return 'plotInterface = buildViz(' + ','.join(params) + ');'

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
		self.assertTrue('<!-- INSERT SEMIOTIC SQUARE -->' in html)
		self.assertTrue('Republican' in html)

	def test_semiotic_square(self):
		semsq = get_test_semiotic_square()
		assembler = self.make_assembler()
		html = assembler.to_html(
			html_base=HTMLSemioticSquareViz(semsq).get_html(num_terms=6))
		if sys.version_info.major == 2:
			self.assertEqual(type(html), unicode)
		else:
			self.assertEqual(type(html), str)
		self.assertFalse('<!-- EXTRA LIBS -->' in html)
		# self.assertFalse('<!-- INSERT SEMIOTIC SQUARE -->' in html)
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
		self.assertTrue(self._https_script_is_present(html))
		self.assertFalse(self._http_script_is_present(html))

	def test_protocol_is_http(self):
		html = self.make_assembler().to_html(protocol='http')
		self.assertFalse(self._https_script_is_present(html))
		self.assertTrue(self._http_script_is_present(html))

	def _http_script_is_present(self, html):
		return 'src="http://' in html

	def _https_script_is_present(self, html):
		return 'src="https://' in html

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

	def test_full_data(self):
		visualization_data = self.make_adapter()
		full_data = "customFullDataFunction()"
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            full_data=full_data)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({17: full_data}))

	def test_show_top_terms(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            show_top_terms=False)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({18: 'false'}))
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            show_top_terms=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({18: 'true'}))
		self.assertEqual((HTMLVisualizationAssembly(visualization_data)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({18: 'true'}))

	def test_show_neutral(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({19: 'false'}))
		self.assertEqual((HTMLVisualizationAssembly(visualization_data, show_neutral=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({19: 'true'}))

	def test_get_tooltip_content(self):
		visualization_data = self.make_adapter()
		f = '''(function(x) {return 'Original X: ' + x.ox;})'''
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            get_tooltip_content=f)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({20: f}))

	def test_x_axis_labels(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            x_axis_values=[1, 2, 3])
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({21: "[1, 2, 3]"}))

	def test_x_axis_labels(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            y_axis_values=[4, 5, 6])
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({22: "[4, 5, 6]"}))

	def test_color_func(self):
		visualization_data = self.make_adapter()
		color_func = 'function colorFunc(d) {var c = d3.hsl(d3.interpolateRdYlBu(d.x)); c.s *= d.y;	return c;}'
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            color_func=color_func)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({23: color_func}))

	def test_show_axes(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            show_axes=False)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({24: 'false'}))

	def test_show_extra(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            show_extra=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({25: 'true'}))

	def test_do_censor_points(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            do_censor_points=False)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({26: 'false'}))

	def test_center_label_over_points(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            center_label_over_points=True)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({27: 'true'}))

	def test_x_axis_labels_over_points(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            x_axis_labels=['Lo', 'Hi'])
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({28: '["Lo", "Hi"]'}))

	def test_y_axis_labels_over_points(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            y_axis_labels=['Lo', 'Hi'])
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({29: '["Lo", "Hi"]'}))

	def test_topic_model_preview_size(self):
		visualization_data = self.make_adapter()
		self.assertEqual((HTMLVisualizationAssembly(visualization_data,
		                                            topic_model_preview_size=20)
		                  ._call_build_visualization_in_javascript()),
		                 self.get_params({30: '20'}))

	def test_vertical_lines(self):
		visualization_data = self.make_adapter()
		params = (HTMLVisualizationAssembly(visualization_data,
		                           vertical_lines=[20, 31])
		 ._call_build_visualization_in_javascript())
		self.assertEqual(params,
		                 self.get_params({31: '[20, 31]'}))

	def test_horizontal_line_y_position(self):
		visualization_data = self.make_adapter()
		params = (HTMLVisualizationAssembly(visualization_data,
											horizontal_line_y_position=0)
		 ._call_build_visualization_in_javascript())
		self.assertEqual(params, self.get_params({32: '0'}))

	def test_vertical_line_x_position(self):
		visualization_data = self.make_adapter()
		params = (HTMLVisualizationAssembly(visualization_data,
											vertical_line_x_position=3)
		 ._call_build_visualization_in_javascript())
		self.assertEqual(params, self.get_params({33: '3'}))
