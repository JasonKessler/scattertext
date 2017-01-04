import pkgutil


class InvalidProtocolException(Exception):
	pass


class HTMLVisualizationAssembly:
	def __init__(self,
	             visualization_data,
	             width_in_pixels=None,
	             height_in_pixels=None,
	             max_snippets=None):
		'''
		:param visualization_data: VisualizationData
		:param width_in_pixels: int, width of viz in pixels, if None, default to JS's choice
		:param height_in_pixels: int, height of viz in pixels, if None, default to JS's choice
		:param max_snippets: int or None, max snippets to snow when temr is clicked, if None show all
		'''
		self._visualization_data = visualization_data
		self._width_in_pixels = width_in_pixels
		self._height_in_pixels = height_in_pixels
		self._max_snippets = max_snippets

	def to_html(self, protocol='http'):
		self._ensure_valid_protocol(protocol)
		javascript_to_insert = '\n'.join([
			self._full_content_of_javascript_files(),
			self._visualization_data.to_javascript(),
			self._call_build_visualization_in_javascript()
		])
		html_file = (self._full_content_of_html_file()
		             .replace('<!-- INSERT SCRIPT -->', javascript_to_insert, 1)
		             .replace('http://', protocol + '://'))
		return html_file

	def _ensure_valid_protocol(self, protocol):
		if protocol not in ('https', 'http'):
			raise InvalidProtocolException(
				"Invalid protocol: %s.  Protocol must be either http or https." % (protocol))

	def _full_content_of_html_file(self):
		return pkgutil.get_data('scattertext',
		                        'data/viz/scattertext.html').decode('utf-8')

	def _full_content_of_javascript_files(self):
		return '\n'.join([pkgutil.get_data('scattertext',
		                                   'data/viz/scripts/' + script_name).decode('utf-8')
		                  for script_name in ['range-tree.js',
		                                      'main.js']])

	def _call_build_visualization_in_javascript(self):
		def js_default_value(x):
			return 'undefined' if x is None else str(x)
		def js_default_value_to_null(x):
			return 'null' if x is None else str(x)

		return 'buildViz(' \
		       + js_default_value(self._width_in_pixels) + ',' \
		       + js_default_value(self._height_in_pixels)+ ',' \
		       + js_default_value_to_null(self._max_snippets) \
		       + ');'
