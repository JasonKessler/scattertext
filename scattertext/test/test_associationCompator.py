from unittest import TestCase
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor, AssociationCompactorByRank, \
    TermCategoryRanker
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix


class TestAssociationCompactor(TestCase):
    def test_compact(self):
        term_doc_mat = get_hamlet_term_doc_matrix()
        new_tdm = AssociationCompactor(max_terms=213).compact(term_doc_mat)
        self.assertEqual(len(term_doc_mat.get_terms()), 26875)
        self.assertEqual(len(new_tdm.get_terms()), 213)

    def test_get_term_ranks(self):
        term_doc_mat = get_hamlet_term_doc_matrix()
        ranks = TermCategoryRanker().get_rank_df(term_doc_mat)
        self.assertEqual(len(ranks), term_doc_mat.get_num_terms())
        self.assertGreaterEqual(ranks.min().min(), 0)

    def test_compact_by_rank(self):
        term_doc_mat = get_hamlet_term_doc_matrix()
        compact_tdm4 = AssociationCompactorByRank(rank=4).compact(term_doc_mat)
        compact_tdm8 = AssociationCompactorByRank(rank=8).compact(term_doc_mat)
        self.assertLess(compact_tdm4.get_num_terms(), compact_tdm8.get_num_terms())
        self.assertLess(compact_tdm8.get_num_terms(), term_doc_mat.get_num_terms())

    def test_get_max_rank(self):
        term_doc_mat = get_hamlet_term_doc_matrix()
        self.assertEqual(TermCategoryRanker().get_max_rank(term_doc_mat), 322)