import numpy as np

from scattertext.domain.CombineDocsIntoDomains import CombineDocsIntoDomains


class NeedsMaxOrMinDomainCountException(Exception):
	pass


class DomainCompactor(object):
	def __init__(self, doc_domains, min_domain_count=None, max_domain_count=None):
		'''

		Parameters
		----------
		doc_domains : np.array like
			Length of documents in corpus. Specifies a single domain for each document.
		min_domain_count : int, None
			Term should appear in at least this number of domains
			Default 0
		max_domain_count : int, None
			Term should appear in at most this number of domains
			Default is the number of domains in doc_domains
		'''
		self.doc_domains = doc_domains
		if max_domain_count is None and min_domain_count is None:
			raise NeedsMaxOrMinDomainCountException(
				"Either max_domain_count or min_domain_count must be entered"
			)
		self.min_domain_count = (0 if min_domain_count is None
		                         else min_domain_count)
		self.max_domain_count = (len(doc_domains) if max_domain_count is None
		                         else max_domain_count)

	def compact(self, term_doc_matrix, non_text=False):
		'''
		Parameters
		----------
		term_doc_matrix : TermDocMatrix
			Term document matrix object to compact

		Returns
		-------
		New term doc matrix
		'''
		domain_mat = CombineDocsIntoDomains(term_doc_matrix).get_new_term_doc_mat(self.doc_domains, non_text)
		domain_count = (domain_mat > 0).sum(axis=0)
		valid_term_mask = (self.max_domain_count >= domain_count) \
		                  & (domain_count >= self.min_domain_count)
		indices_to_compact = np.arange(self._get_num_terms(term_doc_matrix, non_text))[~valid_term_mask.A1]
		return term_doc_matrix.remove_terms_by_indices(indices_to_compact, non_text=non_text)

	def _get_num_terms(self, term_doc_matrix, non_text):
		return term_doc_matrix.get_num_metadata() if non_text else term_doc_matrix.get_num_terms()
