from unittest import TestCase

from scattertext.test.test_semioticSquare import get_test_semiotic_square
from scattertext.viz.HTMLSemioticSquareViz import HTMLSemioticSquareViz


class TestHTMLSemioticSquareViz(TestCase):
	def test_get_html(self):
		semsq = get_test_semiotic_square()
		html_default = HTMLSemioticSquareViz(semsq).get_html()
		html_6 = HTMLSemioticSquareViz(semsq).get_html(num_terms=6)
		self.assertNotEqual(html_default, html_6)