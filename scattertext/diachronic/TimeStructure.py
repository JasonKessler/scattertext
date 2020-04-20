from scattertext.graphs.GraphStructure import GraphStructure


class TimeStructure(GraphStructure):
    def __init__(self,
                 scatterplot_structure,
                 graph_renderer,
                 scatterplot_width=500,
                 scatterplot_height=700,
                 d3_url_struct=None,
                 protocol='http',
                 template_file_name='time_plot.html'):
        GraphStructure.__init__(self,
                                scatterplot_structure,
                                graph_renderer,
                                scatterplot_width,
                                scatterplot_height,
                                d3_url_struct,
                                protocol, template_file_name)

    def _replace_html_template(self, autocomplete_css, html_template, javascript_to_insert):
        html_template = html_template.replace(
            '<!-- EXTRA LIBS -->',
            "<script src='../scattertext/scattertext/data/viz/scripts/timelines-chart.js'></script>\n<!--D3URL-->"
        )
        return GraphStructure._replace_html_template(self, autocomplete_css, html_template, javascript_to_insert)
