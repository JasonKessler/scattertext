import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline

from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.termscoring.RankDifference import RankDifference


class SentencesForTopicModeling(object):
	'''
	Creates a topic model from a set of key terms based on sentence level co-occurrence.
	'''

	def __init__(self, corpus, use_offsets=False):
		'''

		Parameters
		----------
		corpus
		use_offsets

		'''
		assert isinstance(corpus, ParsedCorpus)
		self.corpus = corpus
		self.use_offsets = use_offsets

		if not use_offsets:
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
		else:
			self.termidxstore = corpus._metadata_idx_store
			doc_sent_offsets = [
				pd.IntervalIndex.from_breaks([sent[0].idx for sent in doc.sents] + [len(str(doc))], closed='left')
				for doc_i, doc
				in enumerate(corpus.get_parsed_docs())
			]

			doc_sent_count = []
			tally = 0
			for doc_offsets in doc_sent_offsets:
				doc_sent_count.append(tally)
				tally += len(doc_offsets)

			matfact = CSRMatrixFactory()
			for term, term_offsets in corpus.get_offsets().items():
				term_index = corpus.get_metadata_index(term)
				for doc_i, offsets in term_offsets.items():
					for offset in offsets:
						doc_sent_i = doc_sent_offsets[doc_i].get_loc(offset[0]) + doc_sent_count[doc_i]
						matfact[doc_sent_i, term_index] = 1

			self.sentX = matfact.get_csr_matrix()

	def get_sentence_word_mat(self):
		return self.sentX.astype(np.double).tocoo()

	def get_topic_weights_df(self, pipe=None) -> pd.DataFrame:
		pipe = self._fit_model(pipe)
		return pd.DataFrame(pipe._final_estimator.components_.T,
							index=self.corpus.get_terms(use_metadata=self.use_offsets))

	def get_topics_from_model(
			self,
			pipe=None,
			num_terms_per_topic=10) -> dict:
		'''

		Parameters
		----------
		pipe : Pipeline
			For example, `Pipeline([
				('tfidf', TfidfTransformer(sublinear_tf=True)),
				('nmf', (NMF(n_components=30, l1_ratio=.5, random_state=0)))])`
			The last transformer must populate a `components_` attribute when finished.
		num_terms_per_topic : int

		Returns
		-------
		dict: {term: [term1, ...], ...}
		'''
		pipe = self._fit_model(pipe)
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

	def _fit_model(self, pipe):
		if pipe is None:
			pipe = Pipeline([('tfidf', TfidfTransformer(sublinear_tf=True)),
							 ('nmf', (NMF(n_components=30, l1_ratio=.5, random_state=0)))])
		pipe.fit_transform(self.sentX)
		return pipe

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
