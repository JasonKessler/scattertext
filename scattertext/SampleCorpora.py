# Helper functions for loading political convention data set
import json, sys, re
if sys.version_info[0] >= 3:
	from urllib.request import urlopen
else:
	from urllib2 import urlopen

import pandas as pd


class ConventionData2012(object):
	@staticmethod
	def _speaker_name_factory():
		name_re = re.compile(r'.*(\n|^)(?P<name>[A-Z0-9 ]+):\w*.+', re.M)

		def speaker_name(text):
			for _, name in name_re.findall(text):
				if name not in ('ANNOUNCER', 'AUDIENCE MEMBER', 'AUDIENCE MEMBERS'):
					return name

		return speaker_name

	@staticmethod
	def _clean_function_factory():
		only_speaker_text_re = re.compile(
			r'((^|\n)((ANNOUNCER|AUDIENCE MEMBERS?): .+)($|\n)|(\n|^)((([A-Z\.()\- ]+): ))|\(.+\) *)',
			re.M)
		assert only_speaker_text_re.sub('', 'AUDIENCE MEMBERS: (Chanting.) USA! USA! USA! USA!') == ''
		assert only_speaker_text_re.sub('', 'AUDIENCE MEMBER: (Chanting.) USA! USA! USA! USA!') == ''
		assert only_speaker_text_re.sub('', 'ANNOUNCER: (Chanting.) USA! USA! USA! USA!') == ''
		assert only_speaker_text_re.sub('', 'TOM SMITH: (Chanting.) USA! USA! USA! USA!') == 'USA! USA! USA! USA!'
		assert only_speaker_text_re.sub('', 'DONALD TRUMP: blah blah blah!') == 'blah blah blah!'
		assert only_speaker_text_re.sub('', 'HILLARY CLINTON: (something parenthetical) blah blah blah!') == 'blah blah blah!'
		assert only_speaker_text_re.sub \
			       ('',
			        'ANNOUNCER: (Chanting.) USA! USA! USA! USA!\nTOM SMITH: (Chanting.) ONLY INCLUDE THIS! ONLY KEEP THIS! \nAUDIENCE MEMBER: (Chanting.) USA! USA! USA! USA!').strip() \
		       == 'ONLY INCLUDE THIS! ONLY KEEP THIS!'

		def clean_document(text):
			return only_speaker_text_re.sub('', text)

		return clean_document

	@staticmethod
	def _convention_speech_iter():
		url = 'https://gitcdn.xyz/repo/JasonKessler/scattertext/master/scattertext/data/political_data.json'
		return json.loads(urlopen(url).read().decode('utf-8'))

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
