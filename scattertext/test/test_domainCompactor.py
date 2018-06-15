from unittest import TestCase

import numpy as np

from scattertext import DomainCompactor
from scattertext.termcompaction.DomainCompactor import NeedsMaxOrMinDomainCountException
from scattertext.test.test_TermDocMat import get_hamlet_term_doc_matrix


class TestDomainCompactor(TestCase):
	def test_compact(self):
		hamlet = get_hamlet_term_doc_matrix()
		domains = np.arange(hamlet.get_num_docs()) % 3
		with self.assertRaises(NeedsMaxOrMinDomainCountException):
			hamlet_compact = hamlet.compact(DomainCompactor(domains))

		hamlet_compact = hamlet.compact(DomainCompactor(domains, min_domain_count=2))
		self.assertLess(hamlet_compact.get_num_terms(), hamlet.get_num_terms())
		self.assertEqual(hamlet_compact.get_num_docs(), hamlet.get_num_docs())

		hamlet_compact = hamlet.compact(DomainCompactor(domains, max_domain_count=2))
		self.assertLess(hamlet_compact.get_num_terms(), hamlet.get_num_terms())
		self.assertEqual(hamlet_compact.get_num_docs(), hamlet.get_num_docs())

		hamlet_compact = hamlet.compact(DomainCompactor(domains, max_domain_count=2, min_domain_count=2))
		self.assertLess(hamlet_compact.get_num_terms(), hamlet.get_num_terms())
		self.assertEqual(hamlet_compact.get_num_docs(), hamlet.get_num_docs())
