import pkgutil


class InvalidProtocolException(Exception):
	pass


class HTMLVisualizationAssembly:
	def __init__(self,
	             visualization_data,
	             width_in_pixels=None,
	             height_in_pixels=None,
	             max_snippets=None,
	             color=None,
	             grey_zero_scores=False,
	             sort_by_dist=True,
	             use_full_doc=False,
	             chinese_mode=False,
	             use_non_text_features=False,
	             show_characteristic=True):
		'''

		Parameters
		----------
		visualization_data : dict
			From ScatterChart or a descendant
		width_in_pixels : int, optional
			width of viz in pixels, if None, default to JS's choice
		height_in_pixels : int, optional
			height of viz in pixels, if None, default to JS's choice
		max_snippets : int, optional
			max snippets to snow when temr is clicked, Defaults to show all
		color : str, optional
		  d3 color scheme
		grey_zero_scores : bool, optional
		  If True, color points with zero-scores a light shade of grey.  False by default.
		sort_by_dist : bool, optional
			sort by distance or score, default True
		use_full_doc : bool, optional
			use full document instead of sentence in snippeting
		use_non_text_features : bool, default False
			Show non-bag-of-words features (e.g., Empath) instaed of text.  False by default.
		show_characteristic: bool, default True
			Show characteristic terms on the far left-hand side of the visualization
		'''
		self._visualization_data = visualization_data
		self._width_in_pixels = width_in_pixels
		self._height_in_pixels = height_in_pixels
		self._max_snippets = max_snippets
		self._color = color
		self._sort_by_dist = sort_by_dist
		self._use_full_doc = use_full_doc
		self._chinese_mode = chinese_mode
		self._grey_zero_scores = grey_zero_scores
		self._use_non_text_features = use_non_text_features
		self._show_characteristic = show_characteristic

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
		                  for script_name in ['rectangle-holder.js',  # 'range-tree.js',
		                                      'main.js']])

	def _call_build_visualization_in_javascript(self):
		def js_default_value(x):
			return 'undefined' if x is None else str(x)

		def js_default_value_to_null(x):
			return 'null' if x is None else str(x)

		def js_bool(x):
			return 'true' if x else 'false'

		arguments = [js_default_value(self._width_in_pixels),
		             js_default_value(self._height_in_pixels),
		             js_default_value_to_null(self._max_snippets),
		             js_default_value_to_null(self._color),
		             js_bool(self._sort_by_dist),
		             js_bool(self._use_full_doc),
		             js_bool(self._grey_zero_scores),
		             js_bool(self._chinese_mode),
		             js_bool(self._use_non_text_features),
		             js_bool(self._show_characteristic)]
		return 'buildViz(' + ','.join(arguments) + ');'
