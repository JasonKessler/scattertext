import json

from scattertext.Common import DEFAULT_DIV_ID, DEFAULT_D3_AXIS_VALUE_FORMAT


class InvalidProtocolException(Exception):
    pass


class ScatterplotStructure(object):
    def __init__(
            self,
            visualization_data,
            width_in_pixels=None,
            height_in_pixels=None,
            max_snippets=None,
            color=None,
            grey_zero_scores=False,
            sort_by_dist=True,
            reverse_sort_scores_for_not_category=True,
            use_full_doc=False,
            asian_mode=False,
            match_full_line=False,
            use_non_text_features=False,
            show_characteristic=True,
            word_vec_use_p_vals=False,
            max_p_val=0.1,
            save_svg_button=False,
            p_value_colors=False,
            x_label=None,
            y_label=None,
            full_data=None,
            show_top_terms=True,
            show_neutral=False,
            get_tooltip_content=None,
            x_axis_values=None,
            y_axis_values=None,
            color_func=None,
            show_axes=True,
            horizontal_line_y_position=None,
            vertical_line_x_position=None,
            show_extra=False,
            do_censor_points=True,
            center_label_over_points=False,
            x_axis_labels=None,
            y_axis_labels=None,
            topic_model_preview_size=10,
            vertical_lines=None,
            unified_context=False,
            show_category_headings=True,
            highlight_selected_category=False,
            show_cross_axes=True,
            div_name=DEFAULT_DIV_ID,
            alternative_term_func=None,
            include_all_contexts=False,
            show_axes_and_cross_hairs=False,
            x_axis_values_format=None,
            y_axis_values_format=None,
            max_overlapping=-1,
            show_corpus_stats=True,
            sort_doc_labels_by_name=False,
            always_jump=True,
            show_diagonal=False,
            enable_term_category_description=True,
            use_global_scale=False,
            get_custom_term_html=None,
            header_names=None,
            header_sorting_algos=None,
            ignore_categories=False,
            background_labels=None,
            label_priority_column=None,
            text_color_column=None,
            suppress_text_column=None,
            censor_point_column=None,
            background_color=None,
            right_order_column=None,
            subword_encoding=None,
            top_terms_length=14,
            top_terms_left_buffer=0
    ):
        '''

        Parameters
        ----------
        visualization_data : VizDataAdapter
            From ScatterChart or a descendant
        width_in_pixels : int, optional
            width of viz in pixels, if None, default to 1000
        height_in_pixels : int, optional
            height of viz in pixels, if None, default to 600
        max_snippets : int, optional
            max snippets to snow when term is clicked, Defaults to show all
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
        max_p_val : float, default = 0.1
            Max p-val to use find set of terms for similarity calculation, if
            word_vec_use_p_vals is True.
        save_svg_button : bool, default False
            Add a save as SVG button to the page.
        p_value_colors : bool, default False
          Color points differently if p val is above 1-max_p_val, below max_p_val, or
           in between.
        x_label : str, default None
            If present, use as the x-axis label
        y_label : str, default None
            If present, use as the y-axis label
        full_data : str, default None
            Data used to create chart. By default "getDataAndInfo()".
        show_top_terms : bool, default True
            Show the top terms sidebar
        show_neutral : bool, default False
            Show a third column for matches in neutral documents
        get_tooltip_content : str, default None
            Javascript function to control content of tooltip.  Function takes a parameter
            which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
            returns a string.
        x_axis_values : list, default None
            Numeric value-labels to show on x-axis which correspond to original x-values.
        y_axis_values : list, default None
            Numeric Value-labels to show on y-axis which correspond to original y-values.
        color_func : str, default None
            Javascript function to control color of a point.  Function takes a parameter
            which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
            returns a string.
        show_axes : bool, default True
            Show x and y axes
        horizontal_line_y_position : float, default None
            If x and y axes markers are shown, the position of the horizontal axis marker
        vertical_line_x_position : float, default None
            If x and y axes markers are shown, the position of the vertical axis marker
        show_extra : bool, default False
            Show extra fourth column
        do_censor_points  : bool, default True
            Don't label over dots
        center_label_over_points : bool, default False
            Only put labels centered over point
        x_axis_labels: list, default None
            List of string value-labels to show at evenly spaced intervals on the x-axis.
            Low, medium, high are defaults. This relies on d3's ticks function, which can
            behave unpredictable. Caveat usor.
        y_axis_labels : list, default None
            List of string value-labels to show at evenly spaced intervals on the y-axis.
            Low, medium, high are defaults.  This relies on d3's ticks function, which can
            behave unpredictable. Caveat usor.
        topic_model_preview_size : int, default 10
            If topic models are being visualized, show the first topic_model_preview_size topics
            in a preview.
        vertical_lines: list, default None
            List of scaled points along the x-axis to draw horizontal lines
        unified_context: bool, default False
            Display all context in a single column.
        show_category_headings: bool, default True
            If unified_context, should we show the category headings?
        highlight_selected_category: bool, default False
            Highlight selected category in unified view
        show_cross_axes: bool, default True
            If show_axes is False, do we show cross-axes?
        div_name: str, default DEFAULT_DIV_ID
            Div which holds scatterplot
        alternative_term_func: str, default None
            Javascript function which take a term JSON object and returns a bool.  If the return value is true,
            execute standard term click pipeline. Ex.: `'(function(termDict) {return true;})'`.
        include_all_contexts: bool, default False
            Include all contexts, even non-matching ones, in interface
        show_axes_and_cross_hairs: bool, default False
            Show both cross-axes and peripheral scales.
        x_axis_values_format: str, default None
            d3 format string for x-axis values (see https://github.com/d3/d3-format)
        y_axis_values_format: str, default None
            d3 format string for y-axis values (see https://github.com/d3/d3-format)
        max_overlapping: int, default -1
            Maximum number of overlapping terms to output.  Show all if -1 (default)
        show_corpus_stats: bool, default True
            Populate corpus stats div
        sort_doc_labels_by_name: bool, default False
            If unified document labels, sort the labels by name instead of value.
        always_jump: bool, default True
            Always jump to term contexts if a term is clicked.
        show_diagonal: bool, default False
            Show a diagonal line from the lower-left to the upper-right of the chart
        use_global_scale: bool, default False
            Use the same scaling for the x and y axis. Without this show_diagonal may not
            make sense.
        enable_term_category_description: bool, default True
            List term/metadata statistics under category
        get_custom_term_html: str, default None
            Javascript function which takes term info and outputs custom term HTML
        header_names: Dict[str, str], default None
            Dictionary giving names of term lists shown to the right of the plot. Valid keys are
            upper, lower and right.
        header_sorting_algos: Dict[str, str], default None
            Dictionary giving javascript sorting algorithms for panes. Valid keys are upper, lower
            and right. Value is a JS function which takes the "data" object.
        ignore_categories: bool, default False
            Signals plot should ignore category names.
        background_labels: List[Dict]: default None
            List of [{"Text": "Label", "X": xpos, "Y": ypos}, ...] to be background labels on plot
        label_priority_column : str, default None
            Column in term_metadata_df; larger values in the column indicate a term should be labeled first
        text_color_column: str, default None
            Column in term_metadata_df which supplies term colors
        suppress_text_column: str, default None
            Column in term_metadata_df which is of boolean value. Indicates if a term should be labeled.
        censor_point_column : str, default None
            Should we prevent labels from being drawn over a point?
        right_order_column : str, default None
            Order for right column ("characteristic" by default); largest first
        subword_encoding : str, default None
            Type of subword encoding to use, None if none, currently supports "RoBERTa"
        background_color: str, default None
            Color to set document.body's background
        sentence_piece: bool, default False
            Use sentence piece conventions from to search for terms in JS
        top_terms_length: int, default 14
            Number of top terms to show for left-hand side lists
        top_terms_lefft_buffer: int, default 0
            Number of pixels left to shift top terms list
        '''
        self._visualization_data = visualization_data
        self._width_in_pixels = width_in_pixels if width_in_pixels is not None else 1000
        self._height_in_pixels = height_in_pixels if height_in_pixels is not None else 600
        self._max_snippets = max_snippets
        self._color = color
        self._sort_by_dist = sort_by_dist
        self._use_full_doc = use_full_doc
        self._asian_mode = asian_mode
        self._match_full_line = match_full_line
        self._grey_zero_scores = grey_zero_scores
        self._use_non_text_features = use_non_text_features
        self._show_characteristic = show_characteristic
        self._word_vec_use_p_vals = word_vec_use_p_vals
        self._max_p_val = max_p_val
        self._save_svg_button = save_svg_button
        self._reverse_sort_scores_for_not_category = reverse_sort_scores_for_not_category
        self._p_value_colors = p_value_colors
        self._x_label = x_label
        self._y_label = y_label
        self._full_data = full_data
        self._show_top_terms = show_top_terms
        self._show_neutral = show_neutral
        self._get_tooltip_content = get_tooltip_content
        self._x_axis_values = x_axis_values
        self._y_axis_values = y_axis_values
        self._x_axis_labels = x_axis_labels
        self._y_axis_labels = y_axis_labels
        self._color_func = color_func
        self._show_axes = show_axes
        self._horizontal_line_y_position = horizontal_line_y_position
        self._vertical_line_x_position = vertical_line_x_position
        self._show_extra = show_extra
        self._do_censor_points = do_censor_points
        self._center_label_over_points = center_label_over_points
        self._topic_model_preview_size = topic_model_preview_size
        self._vertical_lines = vertical_lines
        self._unified_context = unified_context
        self._show_category_headings = show_category_headings
        self._highlight_selected_category = highlight_selected_category
        self._show_cross_axes = show_cross_axes
        self._div_name = div_name
        self._alternative_term_func = alternative_term_func
        self._include_all_contexts = include_all_contexts
        self._show_axes_and_cross_hairs = show_axes_and_cross_hairs
        self._x_axis_values_format = x_axis_values_format
        self._y_axis_values_format = y_axis_values_format
        self._max_overlapping = max_overlapping
        self._show_corpus_stats = show_corpus_stats
        self._sort_doc_labels_by_name = sort_doc_labels_by_name
        self._always_jump = always_jump
        self._show_diagonal = show_diagonal
        self._use_global_scale = use_global_scale
        self._enable_term_category_description = enable_term_category_description
        self._get_custom_term_html = get_custom_term_html
        self._header_names = header_names
        self._header_sorting_algos = header_sorting_algos
        self._ignore_categories = ignore_categories
        self._background_labels = background_labels
        self._label_priority_column = label_priority_column
        self._text_color_column = text_color_column
        self._suppress_label_column = suppress_text_column
        self._censor_point_column = censor_point_column
        self._right_order_column = right_order_column
        self._background_color = background_color
        self._subword_encoding = subword_encoding
        self._top_terms_length = top_terms_length
        self._top_terms_left_buffer = top_terms_left_buffer

    def call_build_visualization_in_javascript(self):
        def js_default_value(x, default='undefined'):
            return default if x is None else str(x)

        def js_default_string(x, default_string=None):
            if x is not None:
                return json.dumps(str(x))
            if default_string is None:
                return 'undefined'
            return json.dumps(default_string)

        def js_default_value_to_null(x):
            return 'null' if x is None else str(x)

        def json_or_null(x):
            return 'null' if x is None else json.dumps(x)

        def js_bool(x):
            return 'true' if x else 'false'

        def js_float(x):
            return str(float(x))

        def js_int(x):
            return str(int(x))

        def js_default_full_data(full_data):
            return full_data if full_data is not None else "getDataAndInfo()"

        def json_with_jsvalue_or_null(x):
            if x is None:
                return 'null'
            to_ret = '{'
            first = True
            for key, val in sorted(x.items()):
                if not first: to_ret += ', '
                to_ret += '"%s": %s' % (key, val)
                first = False
            to_ret += '}'
            return to_ret

        arguments = [
            js_default_value(self._width_in_pixels),
            js_default_value(self._height_in_pixels),
            js_default_value_to_null(self._max_snippets),
            js_default_value_to_null(self._color),
            js_bool(self._sort_by_dist),
            js_bool(self._use_full_doc),
            js_bool(self._grey_zero_scores),
            js_bool(self._asian_mode),
            js_bool(self._use_non_text_features),
            js_bool(self._show_characteristic),
            js_bool(self._word_vec_use_p_vals),
            js_bool(self._save_svg_button),
            js_bool(self._reverse_sort_scores_for_not_category),
            js_float(self._max_p_val),
            js_bool(self._p_value_colors),
            js_default_string(self._x_label),
            js_default_string(self._y_label),
            js_default_full_data(self._full_data),
            js_bool(self._show_top_terms),
            js_bool(self._show_neutral),
            js_default_value_to_null(self._get_tooltip_content),
            js_default_value_to_null(self._x_axis_values),
            js_default_value_to_null(self._y_axis_values),
            js_default_value_to_null(self._color_func),
            js_bool(self._show_axes),
            js_bool(self._show_extra),
            js_bool(self._do_censor_points),
            js_bool(self._center_label_over_points),
            json_or_null(self._x_axis_labels),
            json_or_null(self._y_axis_labels),
            js_default_value(self._topic_model_preview_size),
            json_or_null(self._vertical_lines),
            js_default_value_to_null(self._horizontal_line_y_position),
            js_default_value_to_null(self._vertical_line_x_position),
            js_bool(self._unified_context),
            js_bool(self._show_category_headings),
            js_bool(self._show_cross_axes),
            js_default_string(self._div_name),
            js_default_value_to_null(self._alternative_term_func),
            js_bool(self._include_all_contexts),
            js_bool(self._show_axes_and_cross_hairs),
            js_default_string(self._x_axis_values_format, DEFAULT_D3_AXIS_VALUE_FORMAT),
            js_default_string(self._y_axis_values_format, DEFAULT_D3_AXIS_VALUE_FORMAT),
            js_bool(self._match_full_line),
            js_int(self._max_overlapping),
            js_bool(self._show_corpus_stats),
            js_bool(self._sort_doc_labels_by_name),
            js_bool(self._always_jump),
            js_bool(self._highlight_selected_category),
            js_bool(self._show_diagonal),
            js_bool(self._use_global_scale),
            js_bool(self._enable_term_category_description),
            js_default_value_to_null(self._get_custom_term_html),
            json_or_null(self._header_names),
            json_with_jsvalue_or_null(self._header_sorting_algos),
            js_bool(self._ignore_categories),
            json_or_null(self._background_labels),
            js_default_string(self._label_priority_column),
            js_default_string(self._text_color_column),
            js_default_string(self._suppress_label_column),
            js_default_string(self._background_color),
            js_default_string(self._censor_point_column),
            js_default_string(self._right_order_column),
            js_default_string(self._subword_encoding),
            js_default_value(self._top_terms_length, '14'),
            js_default_value(self._top_terms_left_buffer, '0')
        ]
        return 'buildViz(' + ',\n'.join(arguments) + ');\n'

    def get_js_to_call_build_scatterplot(self, object_name='plotInterface'):
        return object_name + ' = ' + self.call_build_visualization_in_javascript()

    def get_js_to_call_build_scatterplot_with_a_function(self, object_name='plotInterface', function_name=None):
        if function_name is None:
            function_name = 'build' + object_name
        function_text = ('function ' + function_name + '() { return '
                         + self.call_build_visualization_in_javascript() + ';}')
        return function_text + '\n\n' + object_name + ' = ' + function_name + '();'

    def get_js_reset_function(self, values_to_set, functions_to_reset, reset_function_name='reset'):
        '''

        :param functions_to_reset: List[str]
        :param values_to_set: List[str]
        :param reset_function_name: str, default = rest
        :return: str
        '''
        return ('function ' + reset_function_name + '() {'
                + "document.querySelectorAll('.scattertext').forEach(element=>element.innerHTML=null);\n"
                + "document.querySelectorAll('#d3-div-1-corpus-stats').forEach(element=>element.innerHTML=null);\n"
                + ' '.join([value + ' = ' + function_name + '();'
                            for value, function_name
                            in zip(values_to_set, functions_to_reset)])
                + '}')
