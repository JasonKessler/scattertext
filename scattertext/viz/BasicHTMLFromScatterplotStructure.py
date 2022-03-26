import pkgutil
from typing import Tuple

from scattertext.Common import DEFAULT_D3_URL, DEFAULT_D3_SCALE_CHROMATIC, \
    DEFAULT_HTML_VIZ_FILE_NAME, AUTOCOMPLETE_CSS_FILE_NAME, SEARCH_FORM_FILE_NAME
from scattertext.viz.ScatterplotStructure import InvalidProtocolException


class ExternalJSUtilts:
    @staticmethod
    def ensure_valid_protocol(protocol):
        if protocol not in ('https', 'http'):
            raise InvalidProtocolException(
                "Invalid protocol: %s.  Protocol must be either http or https." % (protocol))


class D3URLs:
    def __init__(self, d3_url=None, d3_scale_chromatic_url=None):
        self.d3_url = d3_url
        self.d3_scale_chromatic_url = d3_scale_chromatic_url

    def get_d3_url(self):
        return DEFAULT_D3_URL if self.d3_url is None else self.d3_url

    def get_d3_scale_chromatic_url(self):
        return DEFAULT_D3_SCALE_CHROMATIC if self.d3_scale_chromatic_url is None else self.d3_scale_chromatic_url


class PackedDataUtils:
    @staticmethod
    def full_content_of_default_html_template():
        return PackedDataUtils.get_packaged_html_template_content(DEFAULT_HTML_VIZ_FILE_NAME)

    @staticmethod
    def full_content_of_default_autocomplete_css():
        return PackedDataUtils.get_packaged_html_template_content(AUTOCOMPLETE_CSS_FILE_NAME)

    @staticmethod
    def full_content_of_default_search_form(input_id):
        return PackedDataUtils.get_packaged_html_template_content(SEARCH_FORM_FILE_NAME).replace('{{id}}', input_id)

    @staticmethod
    def full_content_of_javascript_files():
        return PackedDataUtils._load_script_file_names([
            'rectangle-holder.js',  # 'range-tree.js',
            'main.js',
            'autocomplete_definition.js'
        ])

    @staticmethod
    def _load_script_file_names(script_names):
        return '; \n \n '.join([PackedDataUtils.get_packaged_script_content(script_name)
                                for script_name in script_names])

    @staticmethod
    def javascript_post_build_viz(input_id, plot_interface_name):
        return (PackedDataUtils
                ._load_script_file_names(['autocomplete_call.js'])
                .replace('{{id}}', input_id)
                .replace('__plotInterface__', plot_interface_name))

    @staticmethod
    def get_packaged_script_content(file_name):
        return pkgutil.get_data('scattertext',
                                'data/viz/scripts/' + file_name).decode('utf-8')

    @staticmethod
    def get_packaged_html_template_content(file_name):
        return pkgutil.get_data('scattertext',
                                'data/viz/' + file_name).decode('utf-8')


class BasicHTMLFromScatterplotStructure(object):
    def __init__(self, scatterplot_structure):
        '''
        :param scatterplot_structure: ScatterplotStructure
        '''
        self.scatterplot_structure = scatterplot_structure

    def to_html(self,
                protocol='http',
                d3_url=None,
                d3_scale_chromatic_url=None,
                html_base=None,
                search_input_id='searchInput'):
        '''
        Parameters
        ----------
        protocol : str
         'http' or 'https' for including external urls
        d3_url, str
          None by default.  The url (or path) of
          d3, to be inserted into <script src="..."/>
          By default, this is `DEFAULT_D3_URL` declared in `ScatterplotStructure`.
        d3_scale_chromatic_url : str
          None by default.
          URL of d3_scale_chromatic_url, to be inserted into <script src="..."/>
          By default, this is `DEFAULT_D3_SCALE_CHROMATIC` declared in `ScatterplotStructure`.
        html_base : str
            None by default.  HTML of semiotic square to be inserted above plot.
        search_input_id : str
            Id of search input. Default is 'searchInput'.
        Returns
        -------
        str, the html file representation

        '''
        d3_url_struct = D3URLs(d3_url, d3_scale_chromatic_url)
        ExternalJSUtilts.ensure_valid_protocol(protocol)
        javascript_to_insert = '\n'.join([
            PackedDataUtils.full_content_of_javascript_files(),
            self.scatterplot_structure._visualization_data.to_javascript(),
            self.scatterplot_structure.get_js_to_call_build_scatterplot(),
            PackedDataUtils.javascript_post_build_viz(search_input_id, 'plotInterface'),
        ])
        html_template = (PackedDataUtils.full_content_of_default_html_template()
                         if html_base is None
                         else self._format_html_base(html_base))
        html_content = (
            html_template
                .replace('<!-- INSERT SCRIPT -->', javascript_to_insert, 1)
                .replace('<!-- INSERT SEARCH FORM -->',
                         PackedDataUtils.full_content_of_default_search_form(search_input_id), 1)
                .replace('<!--D3URL-->', d3_url_struct.get_d3_url(), 1)
                .replace('<!--D3SCALECHROMATIC-->', d3_url_struct.get_d3_scale_chromatic_url())
            # .replace('<!-- INSERT D3 -->', self._get_packaged_file_content('d3.min.js'), 1)
        )

        '''
        if html_base is not None:
            html_file = html_file.replace('<!-- INSERT SEMIOTIC SQUARE -->',
                                          html_base)
        '''

        extra_libs = ''
        if self.scatterplot_structure._save_svg_button:
            # extra_libs = '<script src="https://cdn.rawgit.com/edeno/d3-save-svg/gh-pages/assets/d3-save-svg.min.js" charset="utf-8"></script>'
            extra_libs = ''

        autocomplete_css = PackedDataUtils.full_content_of_default_autocomplete_css()
        html_content = (html_content
                        .replace('/***AUTOCOMPLETE CSS***/', autocomplete_css, 1)
                        .replace('<!-- EXTRA LIBS -->', extra_libs, 1)
                        .replace('http://', protocol + '://'))

        return html_content

    def _format_html_base(self, html_base):
        height = self.scatterplot_structure._height_in_pixels
        cellheight, cellheightshort = cell_height_and_cell_height_short_from_height(height)
        return (html_base.replace('{width}', str(self.scatterplot_structure._width_in_pixels))
                .replace('{height}', str(height))
                .replace('{cellheight}', str(cellheight))
                .replace('{cellheightshort}', str(cellheightshort)))


def cell_height_and_cell_height_short_from_height(height: int) -> Tuple[int, int]:
    cellheight = int(height * (4.5 / 12))
    cellheightshort = height - 2 * cellheight
    return cellheight, cellheightshort
