import pkgutil
from scattertext.viz.BasicHTMLFromScatterplotStructure import D3URLs, ExternalJSUtilts, PackedDataUtils

GRAPH_VIZ_FILE_NAME = 'graph_plot.html'


class GraphStructure(object):
    def __init__(self,
                 scatterplot_structure,
                 graph_renderer,
                 scatterplot_width=500,
                 scatterplot_height=700,
                 d3_url_struct=None,
                 protocol='http',
                 template_file_name=GRAPH_VIZ_FILE_NAME):
        ''',
        Parameters
        ----------
        scatterplot_structure: ScatterplotStructure
        graph_renderer: GraphRenderer
        scatterplot_width: int
        scatterplot_height: int
        d3_url_struct: D3URLs
        protocol: str
            http or https
        template_file_name: file name to use as template
        '''
        self.graph_renderer = graph_renderer
        self.scatterplot_structure = scatterplot_structure
        self.d3_url_struct = d3_url_struct if d3_url_struct else D3URLs()
        ExternalJSUtilts.ensure_valid_protocol(protocol)
        self.protocol = protocol

        self.scatterplot_width = scatterplot_width
        self.scatterplot_height = scatterplot_height

        self.template_file_name = template_file_name

    def to_html(self):
        '''
        Returns
        -------
        str, the html file representation

        '''
        javascript_to_insert = self._get_javascript_to_insert()
        autocomplete_css = PackedDataUtils.full_content_of_default_autocomplete_css()
        html_template = self._get_html_template()
        html_content = self._replace_html_template(autocomplete_css, html_template, javascript_to_insert)
        return html_content

    def _get_javascript_to_insert(self):
        return '\n'.join([
            PackedDataUtils.full_content_of_javascript_files(),
            self.scatterplot_structure._visualization_data.to_javascript(),
            self.scatterplot_structure.get_js_to_call_build_scatterplot(),
            PackedDataUtils.javascript_post_build_viz('termSearch', 'plotInterface'),
            self.graph_renderer.get_javascript()
        ])

    def _replace_html_template(self, autocomplete_css, html_template, javascript_to_insert):
        return (html_template
                .replace('/***AUTOCOMPLETE CSS***/', autocomplete_css, 1)
                .replace('<!-- INSERT SCRIPT -->', javascript_to_insert, 1)
                .replace('<!--D3URL-->', self.d3_url_struct.get_d3_url(), 1)
                .replace('<!-- INSERT GRAPH -->', self.graph_renderer.get_graph())
                .replace('<!--D3SCALECHROMATIC-->', self.d3_url_struct.get_d3_scale_chromatic_url())
                .replace('http://', self.protocol + '://')
                .replace('{width}', str(self.scatterplot_width))
                .replace('{height}', str(self.scatterplot_height))
                )

    def _get_html_template(self):
        return PackedDataUtils.get_packaged_html_template_content(self.template_file_name)

