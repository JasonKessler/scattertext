import numpy as np
from scipy.sparse import csr_matrix, lil_matrix


class CombineDocsIntoDomains(object):
	def __init__(self, term_doc_matrix):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
		'''
		self.term_doc_matrix = term_doc_matrix

	def get_new_term_doc_mat(self, doc_domains):
		'''
		Combines documents together that are in the same domain

		Parameters
		----------
		doc_domains : array-like

		Returns
		-------
		scipy.sparse.csr_matrix

		'''
		assert len(doc_domains) == self.term_doc_matrix.get_num_docs()
		doc_domain_set = set(doc_domains)
		num_terms = self.term_doc_matrix.get_num_terms()
		num_domains = len(doc_domain_set)
		domain_mat = lil_matrix((num_domains, num_terms), dtype=int)
		X = self.term_doc_matrix.get_term_doc_mat()
		for i, domain in enumerate(doc_domain_set):
			domain_mat[i, :] = X[np.array(doc_domains == domain)].sum(axis=0)
		return domain_mat.tocsr()