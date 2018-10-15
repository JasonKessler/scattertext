import sys
from collections import Counter
from unittest import TestCase


from scattertext import whitespace_nlp
from scattertext.features.FeatsFromOnlyEmpath import FeatsFromOnlyEmpath
from scattertext.features.FeatsFromSpacyDocAndEmpath import FeatsFromSpacyDocAndEmpath


def mock_empath_analyze(doc, **kwargs):
	doc.split()
	return {'disappointment': 0.0, 'violence': 0.0, 'ugliness': 0.0, 'legend': 0.0, 'farming': 0.0, 'hygiene': 0.0,
	        'help': 0.0, 'payment': 0.0, 'pride': 0.0, 'prison': 0.0, 'night': 2.0, 'warmth': 0.0, 'magic': 0.0,
	        'tourism': 0.0, 'play': 0.0, 'fight': 0.0, 'sympathy': 0.0, 'competing': 0.0, 'speaking': 2.0,
	        'politeness': 0.0, 'hipster': 0.0, 'blue_collar_job': 1.0, 'musical': 0.0, 'optimism': 0.0, 'power': 0.0,
	        'reading': 0.0, 'royalty': 0.0, 'noise': 0.0, 'rage': 0.0, 'work': 2.0, 'smell': 0.0, 'shame': 0.0,
	        'medieval': 0.0, 'terrorism': 1.0, 'health': 0.0, 'school': 0.0, 'poor': 1.0, 'money': 0.0, 'politics': 0.0,
	        'pain': 0.0, 'hearing': 0.0, 'rural': 0.0, 'economics': 1.0, 'eating': 0.0, 'leader': 0.0, 'hiking': 0.0,
	        'shape_and_size': 0.0, 'weakness': 0.0, 'friends': 0.0, 'strength': 1.0, 'ocean': 0.0, 'lust': 0.0,
	        'medical_emergency': 0.0, 'restaurant': 0.0, 'death': 0.0, 'morning': 1.0, 'cooking': 0.0, 'banking': 0.0,
	        'dominant_heirarchical': 0.0, 'party': 1.0, 'weapon': 0.0, 'nervousness': 0.0, 'anticipation': 0.0,
	        'hate': 0.0, 'vehicle': 4.0, 'art': 0.0, 'car': 4.0, 'leisure': 0.0, 'air_travel': 0.0, 'traveling': 0.0,
	        'animal': 0.0, 'dispute': 0.0, 'shopping': 1.0, 'monster': 0.0, 'pet': 0.0, 'science': 0.0, 'children': 0.0,
	        'ridicule': 1.0, 'affection': 0.0, 'superhero': 0.0, 'sexual': 0.0, 'celebration': 0.0, 'gain': 0.0,
	        'government': 1.0, 'beach': 0.0, 'law': 0.0, 'childish': 0.0, 'philosophy': 0.0, 'liquid': 0.0, 'fire': 0.0,
	        'war': 0.0, 'timidity': 0.0, 'love': 0.0, 'occupation': 1.0, 'achievement': 0.0, 'worship': 0.0, 'crime': 0.0,
	        'cheerfulness': 0.0, 'cold': 0.0, 'weather': 0.0, 'disgust': 0.0, 'phone': 0.0, 'journalism': 0.0,
	        'sadness': 0.0, 'contentment': 0.0, 'sound': 0.0, 'breaking': 0.0, 'neglect': 0.0, 'listen': 0.0,
	        'divine': 0.0, 'internet': 0.0, 'confusion': 0.0, 'religion': 0.0, 'exotic': 0.0, 'white_collar_job': 1.0,
	        'computer': 0.0, 'envy': 0.0, 'wealthy': 0.0, 'swimming': 0.0, 'ship': 0.0, 'suffering': 0.0, 'college': 0.0,
	        'sleep': 2.0, 'valuable': 0.0, 'real_estate': 0.0, 'sailing': 0.0, 'programming': 0.0, 'zest': 0.0,
	        'anger': 0.0, 'sports': 0.0, 'irritability': 0.0, 'exasperation': 0.0, 'independence': 0.0, 'torment': 0.0,
	        'dance': 0.0, 'order': 0.0, 'urban': 0.0, 'tool': 0.0, 'exercise': 0.0, 'negotiate': 0.0, 'wedding': 0.0,
	        'healing': 0.0, 'business': 1.0, 'social_media': 0.0, 'messaging': 1.0, 'swearing_terms': 0.0,
	        'stealing': 0.0, 'fabric': 0.0, 'driving': 4.0, 'fear': 0.0, 'fun': 1.0, 'office': 1.0, 'communication': 2.0,
	        'vacation': 0.0, 'emotional': 0.0, 'ancient': 0.0, 'music': 0.0, 'domestic_work': 1.0, 'giving': 1.0,
	        'deception': 0.0, 'beauty': 0.0, 'movement': 1.0, 'meeting': 0.0, 'alcohol': 0.0, 'heroic': 0.0, 'plant': 0.0,
	        'technology': 0.0, 'anonymity': 0.0, 'writing': 0.0, 'feminine': 0.0, 'surprise': 0.0, 'kill': 0.0,
	        'water': 0.0, 'joy': 0.0, 'dominant_personality': 0.0, 'toy': 0.0, 'positive_emotion': 1.0, 'appearance': 0.0,
	        'military': 0.0, 'aggression': 0.0, 'negative_emotion': 1.0, 'youth': 0.0, 'injury': 0.0, 'body': 0.0,
	        'clothing': 0.0, 'home': 0.0, 'family': 0.0, 'fashion': 0.0, 'furniture': 0.0, 'attractive': 0.0,
	        'trust': 0.0, 'cleaning': 0.0, 'masculine': 0.0, 'horror': 0.0}


class TestFeatsFsromSpacyDocAndEmpath(TestCase):
	def test_main(self):
		try:
			from mock import Mock
		except:
			from unittest.mock import Mock
		feat_getter = FeatsFromSpacyDocAndEmpath(empath_analyze_function=mock_empath_analyze)
		sys.modules['empath'] = Mock(analyze=mock_empath_analyze)
		FeatsFromSpacyDocAndEmpath()
		doc = whitespace_nlp('Hello this is a document.')
		term_freq = feat_getter.get_feats(doc)
		self.assertEqual(set(term_freq.items()),
		                 set({'document': 1, 'hello': 1, 'is': 1, 'this': 1,
		                      'a document': 1, 'hello this': 1, 'is a': 1,
		                      'a': 1, 'this is': 1}.items()))
		metadata_freq = feat_getter.get_doc_metadata(doc)
		self.assertEqual(metadata_freq['ridicule'], 1)
		self.assertNotIn('empath_fashion', metadata_freq)

	def test_empath_not_presesnt(self):
		sys.modules['empath'] = None
		if sys.version_info.major == 3:
			with self.assertRaisesRegex(Exception,
			                            "Please install the empath library to use FeatsFromSpacyDocAndEmpath."):
				FeatsFromSpacyDocAndEmpath()
		else:
			with self.assertRaises(Exception):
				FeatsFromSpacyDocAndEmpath()


class TestFeatsFromOnlyEmpath(TestCase):
	def test_main(self):
		try:
			from mock import Mock
		except:
			from unittest.mock import Mock

		sys.modules['empath'] = Mock(analyze=mock_empath_analyze)
		FeatsFromOnlyEmpath()
		feat_getter = FeatsFromOnlyEmpath(empath_analyze_function=mock_empath_analyze)
		doc = whitespace_nlp('Hello this is a document.')
		term_freq = feat_getter.get_feats(doc)
		metadata_freq = feat_getter.get_doc_metadata(doc)

		self.assertEqual(term_freq, Counter())
		self.assertEqual(metadata_freq['ridicule'], 1)
		self.assertNotIn('fashion', metadata_freq)
		self.assertNotIn('document', metadata_freq)
		self.assertNotIn('a document', metadata_freq)

	def test_empath_not_presesnt(self):
		sys.modules['empath'] = None
		if sys.version_info.major == 3:
			with self.assertRaisesRegex(Exception,
			                            "Please install the empath library to use FeatsFromSpacyDocAndEmpath."):
				FeatsFromSpacyDocAndEmpath()
		else:
			with self.assertRaises(Exception):
				FeatsFromSpacyDocAndEmpath()
