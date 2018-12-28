from unittest import TestCase
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix


class TestClassPercentageCompactor(TestCase):
    def test_compact(self):
        term_doc_mat = get_hamlet_term_doc_matrix()
        new_tdm = AssociationCompactor(max_terms=213).compact(term_doc_mat)
        self.assertEqual(len(term_doc_mat.get_terms()), 26875)
        self.assertEqual(len(new_tdm.get_terms()), 213)
