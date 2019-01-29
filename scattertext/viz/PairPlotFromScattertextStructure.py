from scattertext.Common import PAIR_PLOT_HTML_VIZ_FILE_NAME
from scattertext.cartegoryprojector.CategoryProjection import CategoryProjection
from scattertext.viz.BasicHTMLFromScatterplotStructure import D3URLs, ExternalJSUtilts, PackedDataUtils
from scattertext.viz.HTMLSemioticSquareViz import get_clickable_lexicon


class PairPlotFromScatterplotStructure(object):
    def __init__(self,
                 category_scatterplot_structure,
                 term_scatterplot_structure,
                 category_projection,
                 category_width,
                 category_height,
                 num_terms=10,
                 d3_url_struct=None,
                 protocol='http'):
        ''',
        Parameters
        ----------
        category_scatterplot_structure: ScatterplotStructure
        term_scatterplot_structure: ScatterplotStructure,
        category_projection: CategoryProjection
        category_height: int
        category_width: int
        num_terms: int, default 10
        d3_url_struct: D3URLs
        protocol: str
            http or https
        '''
        self.category_scatterplot_structure = category_scatterplot_structure
        self.term_scatterplot_structure = term_scatterplot_structure
        assert type(category_projection) == CategoryProjection
        self.category_projection = category_projection
        self.d3_url_struct = d3_url_struct if d3_url_struct else D3URLs()
        ExternalJSUtilts.ensure_valid_protocol(protocol)
        self.protocol = protocol
        self.category_width = category_width
        self.category_height = category_height
        self.num_terms = num_terms

    def to_html(self):
        '''
        Returns
        -------
        str, the html file representation

        '''
        javascript_to_insert = '\n'.join([
            PackedDataUtils.full_content_of_javascript_files(),
            self.category_scatterplot_structure._visualization_data.to_javascript('getCategoryDataAndInfo'),
            self.category_scatterplot_structure.get_js_to_call_build_scatterplot('categoryPlotInterface'),
            self.term_scatterplot_structure._visualization_data.to_javascript('getTermDataAndInfo'),
            self.term_scatterplot_structure.get_js_to_call_build_scatterplot('termPlotInterface'),
        ])
        html_template = PackedDataUtils.get_packaged_html_template_content(PAIR_PLOT_HTML_VIZ_FILE_NAME)
        html_content = (
            html_template
                .replace('<!-- INSERT SCRIPT -->', javascript_to_insert, 1)
                .replace('<!--D3URL-->', self.d3_url_struct.get_d3_url(), 1)
                .replace('<!--D3SCALECHROMATIC-->', self.d3_url_struct.get_d3_scale_chromatic_url())
            # .replace('<!-- INSERT D3 -->', self._get_packaged_file_content('d3.min.js'), 1)
        )
        html_content = (html_content.replace('http://', self.protocol + '://'))
        axes_labels = self.category_projection.get_nearest_terms(num_terms=self.num_terms)
        for position in ['left', 'right', 'top', 'bottom', 'top_left', 'top_right', 'bottom_left', 'bottom_right']:
            html_content = html_content.replace(
                '{%s}' % (position),
                get_clickable_lexicon(
                    axes_labels[position],
                    'termPlotInterface'
                ) if position in axes_labels else ''
            )
        return html_content.replace('{width}', str(self.category_width)).replace('{height}', str(self.category_height))
