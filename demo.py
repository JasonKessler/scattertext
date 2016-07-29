import json
import os
import pkgutil
import re

from scattertext import TermDocMatrixFactory



def clean_function_factory():
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

def convention_speech_iter():
		relative_path = os.path.join('data', 'political_data.json')
		try:
			cwd = os.path.dirname(os.path.abspath(__file__))
			path = os.path.join(cwd, relative_path)
			return json.load(path)
		except:
			return json.loads(pkgutil.get_data('scattertext', relative_path))

def main():
	def make_category_text_iter():
		for speaker_obj in convention_speech_iter():
			political_party = speaker_obj['name']
			for speech in speaker_obj['speeches']:
				yield political_party, speech

	TermDocMatrixFactory(
		category_text_iter=make_category_text_iter(),
		clean_function=clean_function_factory()
	).build()

