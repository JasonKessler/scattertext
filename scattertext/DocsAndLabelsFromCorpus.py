import numpy as np
import sys

from scattertext import TermCategoryFrequencies, CorpusDF
from scattertext.Corpus import Corpus
from scattertext.ParsedCorpus import ParsedCorpus


class CorpusShouldBeParsedCorpusException(Exception):
	pass


class DocsAndLabelsFromCorpus:
	def __init__(self, corpus, alternative_text_field=None):
		'''
		Parameters
		----------
		corpus, Corpus: Corpus to extract documents and labels from
		alternative_text_field, str or None: if str, corpus must be parsed corpus
		'''
		#assert (isinstance(corpus, (Corpus, ParsedCorpus, CorpusDF, TermCategoryFrequencies))
		#		or (issubclass(type(corpus), (Corpus, ParsedCorpus, CorpusDF, TermCategoryFrequencies))))
		self._texts_to_display = None
		if alternative_text_field is not None:
			if not isinstance(corpus, ParsedCorpus):
				raise CorpusShouldBeParsedCorpusException(
					'Corpus type needs to be ParsedCorpus to use the alternative text field.')
			self._texts_to_display = corpus.get_field(alternative_text_field)
		self._use_non_text_features = False
		self._corpus = corpus

	def use_non_text_features(self):
		self._use_non_text_features = True
		return self

	def get_labels_and_texts(self):
		# type: () -> dict
		texts = self._get_texts_to_display()
		to_ret = {'categories': self._corpus.get_categories(),
		          'labels': self._corpus.get_doc_indices(),
		          'texts': self._get_list_from_texts(texts)}
		if self._use_non_text_features:
			to_ret['extra'] = self._corpus.list_extra_features()
		return to_ret

	def _get_list_from_texts(self, texts):
		if sys.version_info[0] == 2:
			return texts.astype(unicode).tolist()
		else:
			return texts.astype(str).tolist()

	def _get_texts_to_display(self):
		if self._there_are_no_alternative_texts_to_display():
			return self._corpus.get_texts()
		else:
			return self._texts_to_display

	def _there_are_no_alternative_texts_to_display(self):
		return self._texts_to_display is None

	def get_labels_and_texts_and_meta(self, metadata):
		# type: (np.array) -> dict
		data = self.get_labels_and_texts()
		assert len(metadata) == len(data['labels'])
		data['meta'] = list(metadata)
		return data


class DocsAndLabelsFromCorpusSample(DocsAndLabelsFromCorpus):
	def __init__(self, corpus, max_per_category, alternative_text_field=None, seed=None):
		DocsAndLabelsFromCorpus.__init__(self, corpus, alternative_text_field)
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
		to_ret = {'categories': self._corpus.get_categories(), 'labels': [], 'texts': []}
		labels = self._corpus._y.astype(int)
		texts = self._get_texts_to_display()
		if self._use_non_text_features:
			to_ret['extra'] = []
			extrafeats = self._corpus.list_extra_features()
		if metadata is not None:
			to_ret['meta'] = []
		for label_i in range(len(self._corpus._category_idx_store)):
			label_indices = np.arange(0, len(labels))[labels == label_i]
			if self.max_per_category < len(label_indices):
				label_indices = np.random.choice(label_indices, self.max_per_category, replace=False)
				to_ret['labels'] += list([int(e) for e in labels[label_indices]])
				to_ret['texts'] += list(texts[label_indices])
				if metadata is not None:
					to_ret['meta'] += [metadata[i] for i in label_indices]
				if self._use_non_text_features:
					to_ret['extra'] += [extrafeats[i] for i in label_indices]

		return to_ret

	def get_labels_and_texts_and_meta(self, metadata):
		return self.get_labels_and_texts(metadata)
