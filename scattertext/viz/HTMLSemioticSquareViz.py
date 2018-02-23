import pkgutil


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

	def _get_table(self, num_terms):
		lexicons = self.semiotic_square_.get_lexicons(num_terms=num_terms)
		template = self._get_template()
		formatters = {category: self._lexicon_to_html(lexicon)
		             for category, lexicon
		             in lexicons.items()}
		formatters.update(self.semiotic_square_.get_labels())
		for k, v in formatters.items():
			template = template.replace('{' + k + '}', v)
		return template

	def _lexicon_to_html(self, lexicon):
		onclick_js = ('plotInterface.displayTermContexts('
		              + 'plotInterface.gatherTermContexts('
		              + "plotInterface.termDict['{term}']));")
		onmouseover_js = ("plotInterface.showToolTipForTerm('{term}')")
		template = ('<span onclick="' + onclick_js + '"'
		            + ' onmouseover="' + onmouseover_js + '"'
		            + '>{term}</span>')
		return ', '.join(template.format(term=term) for term in lexicon)

	def _get_template(self):
		return pkgutil.get_data('scattertext',
		                        'data/viz/semiotic_new.html').decode('utf-8')
