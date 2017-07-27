from unittest import TestCase

from scattertext.OneClassScatterChart import OneClassScatterChart
from scattertext.test.test_termDocMatrixFactory \
	import build_hamlet_jz_term_doc_mat, build_hamlet_jz_df


class TestOneClassScatterChart(TestCase):
	def test_main(self):
		df = build_hamlet_jz_df()
		# to do
		#scatterchart = OneClassScatterChart(tdm)
		#self.fail()