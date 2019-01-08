from scattertext.Common import PAIR_PLOT_HTML_VIZ_FILE_NAME
from scattertext.viz.BasicHTMLFromScatterplotStructure import D3URLs, ExternalJSUtilts, PackedDataUtils


class PairPlotFromScatterplotStructure(object):
    def __init__(self,
                 category_scatterplot_structure,
                 term_scatterplot_structure,
                 d3_url_struct=None,
                 protocol='http'):
        ''',
        Parameters
        ----------
        category_scatterplot_structure: ScatterplotStructure
        term_scatterplot_structure: ScatterplotStructure
        d3_url_struct: D3URLs
        protocol: str
            http or https
        '''
        self.category_scatterplot_structure = category_scatterplot_structure
        self.term_scatterplot_structure = term_scatterplot_structure
        self.d3_url_struct = d3_url_struct if d3_url_struct else D3URLs()
        ExternalJSUtilts.ensure_valid_protocol(protocol)
        self.protocol = protocol

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
        html_content = (html_content .replace('http://', self.protocol + '://'))
        return html_content