import pkgutil


class InvalidProtocolException(Exception):
	pass


class HTMLVisualizationAssembly:
	def __init__(self, visualization_data,
	             width_in_pixels=None,
	             height_in_pixels=None):
		'''
		:param visualization_data: VisualizationData
		:param width_in_pixels: int, width of viz in pixels, if None, default to JS's choice
		:param height_in_pixels: height, width of viz in pixels, if None, default to JS's choice
		'''
		self._visualization_data = visualization_data
		self._width_in_pixels = width_in_pixels
		self._height_in_pixels = height_in_pixels

	def to_html(self, protocol='http'):
		if protocol not in ('https', 'http'):
			raise InvalidProtocolException("Invalid protocol: %s.  Protocol must be either http or https."
			                               % (protocol))
		html_file = pkgutil.get_data('scattertext',
		                             'data/viz/scattertext.html').decode('utf-8')
		scripts = '\n'.join([pkgutil.get_data('scattertext',
		                                      'data/viz/scripts/' + script_name).decode('utf-8')
		                     for script_name in ['range-tree.js',
		                                         'main.js']])
		viz_data_in_javascript_command_form = self._visualization_data.to_javascript()
		scripts += '\n' + viz_data_in_javascript_command_form
		scripts += '\n' + self._get_build_viz_call()
		html_file = (html_file
		             .replace('<!-- INSERT SCRIPT -->', scripts, 1)
		             .replace('http://', protocol + '://'))
		return html_file

	def _get_build_viz_call(self):
		def js_default_value(x):
			return 'undefined' if x is None else str(x)

		return 'buildViz(' \
		       + js_default_value(self._width_in_pixels) + ',' \
		       + js_default_value(self._height_in_pixels) \
		       + ');'
