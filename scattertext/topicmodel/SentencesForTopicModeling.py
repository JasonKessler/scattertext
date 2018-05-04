import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline

from scattertext import CSRMatrixFactory
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.termscoring.RankDifference import RankDifference


class SentencesForTopicModeling(object):
	'''
	Creates a topic model from a set of key terms based on sentence level co-occurrence.
	'''

	def __init__(self, corpus):
		'''

		Parameters
		----------
		corpus
		'''
		assert isinstance(corpus, ParsedCorpus)
		self.corpus = corpus
		self.termidxstore = corpus._term_idx_store
		matfact = CSRMatrixFactory()
		self.doclabs = []
		self.sentlabs = []
		self.sentdocs = []
		senti = 0
		for doci, doc in enumerate(corpus.get_parsed_docs()):
			for sent in doc.sents:
				validsent = False
				for t in sent:
					try:
						termi = self.termidxstore.getidxstrict(t.lower_)
					except:
						continue
					if validsent is False:
						senti += 1
						self.sentlabs.append(corpus._y[doci])
						self.sentdocs.append(doci)
						validsent = True
					matfact[senti, termi] = 1
		self.sentX = matfact.get_csr_matrix().astype(bool)

	def get_topics_from_model(
			self,
			pipe=Pipeline([
				('tfidf', TfidfTransformer(sublinear_tf=True)),
				('nmf', (NMF(n_components=30, alpha=.1, l1_ratio=.5, random_state=0)))]),
			num_terms_per_topic=10):
		'''

		Parameters
		----------
		pipe : Pipeline
			For example, `Pipeline([
				('tfidf', TfidfTransformer(sublinear_tf=True)),
				('nmf', (NMF(n_components=30, alpha=.1, l1_ratio=.5, random_state=0)))])`
			The last transformer must populate a `components_` attribute when finished.
		num_terms_per_topic : int

		Returns
		-------
		dict: {term: [term1, ...], ...}
		'''
		pipe.fit_transform(self.sentX)

		topic_model = {}
		for topic_idx, topic in enumerate(pipe._final_estimator.components_):
			term_list = [self.termidxstore.getval(i)
			             for i
			             in topic.argsort()[:-num_terms_per_topic - 1:-1]
			             if topic[i] > 0]
			if len(term_list) > 0:
				topic_model['%s. %s' % (topic_idx, term_list[0])] = term_list
			else:
				Warning("Topic %s has no terms with scores > 0. Omitting." % (topic_idx))
		return topic_model

	def get_topics_from_terms(self,
	                          terms=None,
	                          num_terms_per_topic=10,
	                          scorer=RankDifference()):
		'''
		Parameters
		----------
		terms : list or None
			If terms is list, make these the seed terms for the topoics
			If none, use the first 30 terms in get_scaled_f_scores_vs_background
		num_terms_per_topic : int, default 10
			Use this many terms per topic
		scorer : TermScorer
			Implements get_scores, default is RankDifferce, which tends to work best

		Returns
		-------
		dict: {term: [term1, ...], ...}
		'''
		topic_model = {}

		if terms is None:
			terms = self.corpus.get_scaled_f_scores_vs_background().index[:30]

		for term in terms:
			termidx = self.termidxstore.getidxstrict(term)
			labels = self.sentX[:, termidx].astype(bool).todense().A1
			poscnts = self.sentX[labels, :].astype(bool).sum(axis=0).A1
			negcnts = self.sentX[~labels, :].astype(bool).sum(axis=0).A1
			scores = scorer.get_scores(poscnts, negcnts)
			topic_model[term] = [self.termidxstore.getval(i) for i in
			                     np.argsort(-scores)[:num_terms_per_topic]]
		return topic_model
