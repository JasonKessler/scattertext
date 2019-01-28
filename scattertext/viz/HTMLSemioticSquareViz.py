import pkgutil

from scattertext.Common import SEMIOTIC_SQUARE_HTML_PATH


def get_clickable_lexicon(lexicon, plot_interface='plotInterface'):
	onclick_js = "{plot_interface}.displayTermContexts({plot_interface}.data, {plot_interface}.gatherTermContexts(" \
				 "{plot_interface}.termDict['{term}']));"
	onmouseover_js = (
		"{plot_interface}.showToolTipForTerm({plot_interface}.data, {plot_interface}.svg, '{term}',"
		"{plot_interface}.termDict['{term}'])"
	)
	onmouseout_js = "{plot_interface}.tooltip.transition().style('opacity', 0)"
	template = ('<span onclick="' + onclick_js + '" onmouseover="' + onmouseover_js + '" onmouseout="'+
				onmouseout_js +'">{term}</span>')
	return ', \n'.join(template.format(term=term, plot_interface=plot_interface) for term in lexicon)

def get_halo_td_style():
	return '''
			<style>
			td {

	                border-collapse: collapse;
	                box-sizing: border-box;
	                color: rgb(0, 0, 0);
	                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
	                font-size: 12px;
	                height: auto ;
	                line-height: normal;
	                text-align: right;
	                text-size-adjust:100% ;
	                -webkit-border-horizontal-spacing: 0px;
	                -webkit-border-vertical-spacing:0px;
			}
			</style>'''

class HTMLSemioticSquareViz(object):
	def __init__(self, semiotic_square):
		'''
		Parameters
		----------
		semiotic_square : SemioticSquare
		'''
		self.semiotic_square_ = semiotic_square

	def get_html(self, num_terms=10):
		return self._get_style() + self._get_table(num_terms)

	def _get_style(self):
		return get_halo_td_style()

	def _get_table(self, num_terms):
		lexicons = self.semiotic_square_.get_lexicons(num_terms=num_terms)
		template = self._get_template()
		formatters = {category: self._lexicon_to_html(lexicon)
		             for category, lexicon in lexicons.items()}
		formatters.update(self.semiotic_square_.get_labels())
		for k, v in formatters.items():
			template = template.replace('{' + k + '}', v)
		return template

	def _lexicon_to_html(self, lexicon):
		return get_clickable_lexicon(lexicon)

	def _get_template(self):
		return pkgutil.get_data('scattertext', SEMIOTIC_SQUARE_HTML_PATH).decode('utf-8')
