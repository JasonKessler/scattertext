from abc import ABCMeta, abstractmethod


class TermSignificance(object):
	__metaclass__ = ABCMeta
	@abstractmethod
	def get_p_vals(self, X):
		pass