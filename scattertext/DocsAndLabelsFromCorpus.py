import numpy as np

from scattertext.Corpus import Corpus


class DocsAndLabelsFromCorpus:
	def __init__(self, corpus):
		assert (isinstance(corpus, Corpus))
		self.corpus = corpus

	def get_labels_and_texts(self):
		# type: () -> dict
		return {'categories': self.corpus.get_categories(),
		        'labels': self.corpus._y.astype(int).tolist(),
		        'texts': self.corpus.get_texts().tolist()}

	def get_labels_and_texts_and_meta(self, metadata):
		# type: (np.array) -> dict
		data = self.get_labels_and_texts()
		assert len(metadata) == len(data['labels'])
		data['meta'] = list(metadata)
		return data


class DocsAndLabelsFromCorpusSample(DocsAndLabelsFromCorpus):
	def __init__(self, corpus, max_per_category, seed=None):
		DocsAndLabelsFromCorpus.__init__(self, corpus)
		self.max_per_category = max_per_category
		if seed is not None:
			np.random.seed(seed)

	def get_labels_and_texts(self, metadata=None):
		'''
		Parameters
		----------
		metadata : (array like or None)

		Returns
		-------
		{'labels':[], 'texts': []} or {'labels':[], 'texts': [], 'meta': []}
		'''
		to_ret = {'categories': self.corpus.get_categories(), 'labels': [], 'texts': []}
		labels = self.corpus._y.astype(int)
		texts = self.corpus.get_texts()
		if metadata is not None:
			to_ret['meta'] = []
		for label_i in range(len(self.corpus._category_idx_store)):
			label_indices = np.arange(0, len(labels))[labels == label_i]
			if self.max_per_category < len(label_indices):
				label_indices = np.random.choice(label_indices, self.max_per_category, replace=False)
				to_ret['labels'] += list([int(e) for e in labels[label_indices]])
				to_ret['texts'] += list(texts[label_indices])
				if metadata is not None:
					to_ret['meta'] += list(metadata[label_indices])
		return to_ret

	def get_labels_and_texts_and_meta(self, metadata):
		return self.get_labels_and_texts(metadata)
