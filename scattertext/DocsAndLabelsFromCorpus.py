from scattertext.Corpus import Corpus


class DocsAndLabelsFromCorpus:
	def __init__(self, corpus):
		assert(isinstance(corpus, Corpus))
		self.corpus = corpus

	def get_labels_and_texts(self):
		# type: () -> dict
		return {'labels': self.corpus._y.astype(int).tolist(),
		        'texts': self.corpus.get_texts().tolist()}

	def get_labels_and_texts_and_meta(self, metadata):
		# type: (list) -> dict
		data = self.get_labels_and_texts()
		assert len(metadata) == len(data['labels'])
		data['meta'] = metadata
		return data