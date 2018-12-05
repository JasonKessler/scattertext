# Helper functions for loading political convention data set
import bz2
import io
import json
import pkgutil
import re
import sys

from scattertext.Common import POLITICAL_DATA_URL, ROTTEN_TOMATOES_DATA_URL

if sys.version_info[0] >= 3:
	from urllib.request import urlopen
else:
	from urllib2 import urlopen

import pandas as pd


class ConventionData2012(object):
	@staticmethod
	def _speaker_name_factory():
		name_re = re.compile(r'.*(\n|^)(?P<name>[A-Z0-9 \.\']+):\w*.+', re.M)

		def speaker_name(text):
			for _, name in name_re.findall(text):
				if name not in ('ANNOUNCER', 'AUDIENCE MEMBER', 'AUDIENCE MEMBERS'):
					return name

		return speaker_name

	@staticmethod
	def _clean_function_factory():
		only_speaker_text_re = re.compile(
			r'((^|\n)((ANNOUNCER|AUDIENCE MEMBERS?): .+)($|\n)|(\n|^)((([A-Z\.()\-\' ]+): ))|\(.+\) *)',
			re.M)
		assert only_speaker_text_re.sub('', 'AUDIENCE MEMBERS: (Chanting.) USA! USA! USA! USA!') == ''
		assert only_speaker_text_re.sub('', 'AUDIENCE MEMBER: (Chanting.) USA! USA! USA! USA!') == ''
		assert only_speaker_text_re.sub('', 'ANNOUNCER: (Chanting.) USA! USA! USA! USA!') == ''
		assert only_speaker_text_re.sub('', 'TOM SMITH: (Chanting.) USA! USA! USA! USA!') == 'USA! USA! USA! USA!'
		assert only_speaker_text_re.sub('', 'DONALD TRUMP: blah blah blah!') == 'blah blah blah!'
		assert only_speaker_text_re.sub('',
		                                'HILLARY CLINTON: (something parenthetical) blah blah blah!') == 'blah blah blah!'
		assert only_speaker_text_re.sub \
			       ('',
			        'ANNOUNCER: (Chanting.) USA! USA! USA! USA!\nTOM SMITH: (Chanting.) ONLY INCLUDE THIS! ONLY KEEP THIS! \nAUDIENCE MEMBER: (Chanting.) USA! USA! USA! USA!').strip() \
		       == 'ONLY INCLUDE THIS! ONLY KEEP THIS!'

		def clean_document(text):
			return only_speaker_text_re.sub('', text)

		return clean_document

	@staticmethod
	def _convention_speech_iter():
		try:
			data_stream = pkgutil.get_data('scattertext', 'data/political_data.json').decode('utf-8')
		except:
			url = POLITICAL_DATA_URL
			data_stream = urlopen(url).read().decode('utf-8')
		return json.loads(data_stream)

	@staticmethod
	def _iter_party_speech_pairs():
		for speaker_obj in ConventionData2012._convention_speech_iter():
			political_party = speaker_obj['name']
			for speech in speaker_obj['speeches']:
				yield political_party, speech

	@staticmethod
	def get_data():
		clean = ConventionData2012._clean_function_factory()
		get_speaker_name = ConventionData2012._speaker_name_factory()
		data = []
		for party, speech in ConventionData2012._iter_party_speech_pairs():
			cleaned_speech = clean(speech)
			speaker_name = get_speaker_name(speech)
			if cleaned_speech and cleaned_speech != '' and speaker_name != '':
				data.append({'party': party,
				             'text': cleaned_speech,
				             'speaker': speaker_name})
		return pd.DataFrame(data)


class RottenTomatoes(object):
	'''
	Derived from the sentiment polarity/subjectivity datasets from
	http://www.cs.cornell.edu/people/pabo/movie-review-data/

	Bo Pang and Lillian Lee. ``A Sentimental Education: Sentiment Analysis Using Subjectivity
	 Summarization Based on Minimum Cuts'', Proceedings of the ACL, 2004.
	'''

	@staticmethod
	def get_data():
		'''
		Returns
		-------
		pd.DataFrame

		I.e.,
		>>> convention_df.iloc[0]
		category                                                    plot
		filename                 subjectivity_html/obj/2002/Abandon.html
		text           A senior at an elite college (Katie Holmes), a...
		movie_name                                               abandon
		'''
		try:
			data_stream = pkgutil.get_data('scattertext', 'data/rotten_tomatoes_corpus.csv.bz2')
		except:
			url = ROTTEN_TOMATOES_DATA_URL
			data_stream = urlopen(url).read()
		return pd.read_csv(io.BytesIO(bz2.decompress(data_stream)))

	@staticmethod
	def get_full_data():
		'''
		Returns all plots and reviews, not just the ones that appear in movies with both plot descriptions and reviews.

		Returns
		-------
		pd.DataFrame

		I.e.,
		>>> convention_df.iloc[0]
		category                                                             plot
		text                    Vijay Singh Rajput (Amitabh Bachchan) is a qui...
		movie_name                                                        aankhen
		has_plot_and_reviews                                                False
		Name: 0, dtype: object
		'''
		try:
			data_stream = pkgutil.get_data('scattertext', 'data/rotten_tomatoes_corpus_full.csv.bz2')
		except:
			url = ROTTEN_TOMATOES_DATA_URL
			data_stream = urlopen(url).read()
		return pd.read_csv(io.BytesIO(bz2.decompress(data_stream)))
