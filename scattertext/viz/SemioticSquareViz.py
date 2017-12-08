class SemioticSquareViz(object):
	def __init__(self, semiotic_square):
		'''
		Parameters
		----------
		semiotic_square : SemioticSquare
		'''
		self.semiotic_square_ = semiotic_square

	def get_html(self, num_terms=10):
		lexicons = self.semiotic_square_.get_lexicons(num_terms=num_terms)
		template = self._get_template()
		html = template.format(category_a=self.semiotic_square_.category_a_,
		                       category_b=self.semiotic_square_.category_b_,
		                       **{category: ', '.join(lexicon)
		                          for category, lexicon
		                          in lexicons.items()})
		return self._get_style() + html

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
                text-size-adjust:100%
                ;
                //white-space:
                //normal
                //;
                //width: auto;
                -webkit-border-horizontal-spacing: 0px;
                -webkit-border-vertical-spacing:0px;
		}
		</style>'''

	def _get_template(self):
		return '''
    <table cellspacing=0>
		
    <tr style="background: #FFF">
     <td></td>
     <td></td>
     <td style="text-align: center"><b>{category_a} + {category_b}</b>
     <div style="width: 200px">{category_a_and_b_words}</div></td>
     <td></td>
     <td></td>
    </tr>
    <tr style="background: #FFF">
     <td></td>
     <td style="border-top: solid; border-left: solid; text-align: left"><b>{category_a}</b>
     <div style="width: 200px">{category_a_words}</div></td>
     <td style="border-top: solid"></td>
     <td style="border-top: solid; border-right: solid; text-align: right"><b>{category_b}</b>
     <div style="width: 200px">{category_b_words}</div></td>
     <td></td>
    </tr>
    <tr style="background: #FFF">
     <td style="text-align: right"><b>{category_a} + Not {category_b}</b>
     <div style="width: 200px">{category_a_vs_b_words}</div></td>
     <td style="border-left: solid"></td>
     <td></td>
     <td style="border-right: solid"></td>
     <td style="text-align: right"><b>{category_b} + Not {category_a}</b>
     <div style="width: 200px">{category_b_vs_a_words}</div></td>
    </tr>
    <tr style="background: #FFF">
     <td></td>
     <td style="border-bottom: solid; border-left: solid; text-align: left">
     <b>Not {category_b}</b><div style="width: 200px">{not_category_b_words}</div></td>
     <td style="border-bottom: solid;"></td>
     <td style="border-bottom: solid; border-right: solid; text-align: right">
     <b>Not {category_a}</b><div style="width: 200px">{not_category_a_words}</div></td>
     <td></td>
    </tr>
    <tr style="background: #FFF">
     <td></td>
     <td></td>
     <td style="text-align: center"><b>Not {category_a} + Not {category_b}</b>
     <div style="width: 200px">{not_category_a_and_b_words}</div></td>
     <td></td>
     <td></td>
    </tr>
    </table>'''
