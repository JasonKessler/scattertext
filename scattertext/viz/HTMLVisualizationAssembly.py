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
	             reverse_sort_scores_for_not_category=True,
	             use_full_doc=False,
	             chinese_mode=False,
	             use_non_text_features=False,
	             show_characteristic=True,
	             word_vec_use_p_vals=False,
	             max_p_val=0.05,
	             save_svg_button=False):
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
		reverse_sort_scores_for_not_category : bool, optional
			If using a custom score, score the not-category class by
			lowest-score-as-most-predictive. Turn this off for word vectory
			or topic similarity. Default True.
		use_full_doc : bool, optional
			use full document instead of sentence in snippeting
		use_non_text_features : bool, default False
			Show non-bag-of-words features (e.g., Empath) instaed of text.  False by default.
		show_characteristic: bool, default True
			Show characteristic terms on the far left-hand side of the visualization
		word_vec_use_p_vals: bool, default False
			Use category-associated p-values to determine which terms to give word
			vec scores.
		max_p_val : float, default = 0.05
			Max p-val to use find set of terms for similarity calculation, if
			word_vec_use_p_vals is True.
		save_svg_button : bool, default False
			Add a save as SVG button to the page.
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
		self._word_vec_use_p_vals = word_vec_use_p_vals
		self._max_p_val = max_p_val
		self._save_svg_button = save_svg_button
		self._reverse_sort_scores_for_not_category = reverse_sort_scores_for_not_category

	def to_html(self, protocol='http'):
		self._ensure_valid_protocol(protocol)
		javascript_to_insert = '\n'.join([
			self._full_content_of_javascript_files(),
			self._visualization_data.to_javascript(),
			self._call_build_visualization_in_javascript()
		])
		html_file = (self._full_content_of_html_file()
		             .replace('<!-- INSERT SCRIPT -->', javascript_to_insert, 1))
		extra_libs = ''
		if self._save_svg_button:
			# extra_libs = '<script src="https://cdn.rawgit.com/edeno/d3-save-svg/gh-pages/assets/d3-save-svg.min.js" charset="utf-8"></script>'
			extra_libs = ''
		html_file = (html_file
		             .replace('<!-- EXTRA LIBS -->', extra_libs, 1)
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

		def js_float(x):
			return str(float(x))

		arguments = [js_default_value(self._width_in_pixels),
		             js_default_value(self._height_in_pixels),
		             js_default_value_to_null(self._max_snippets),
		             js_default_value_to_null(self._color),
		             js_bool(self._sort_by_dist),
		             js_bool(self._use_full_doc),
		             js_bool(self._grey_zero_scores),
		             js_bool(self._chinese_mode),
		             js_bool(self._use_non_text_features),
		             js_bool(self._show_characteristic),
		             js_bool(self._word_vec_use_p_vals),
		             js_bool(self._save_svg_button),
		             js_bool(self._reverse_sort_scores_for_not_category),
		             js_float(self._max_p_val)]
		return 'buildViz(' + ','.join(arguments) + ');'
