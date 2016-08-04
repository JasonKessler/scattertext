from __future__ import print_function

import json
import os
import pkgutil
import re

from scattertext import ScatterChart
from scattertext import TermDocMatrixFactory
from scattertext.FastButCrapNLP import fast_but_crap_nlp
from scattertext.Scalers import percentile_ordinal


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

	return clean_document


def convention_speech_iter():
	relative_path = os.path.join('scattertext/data', 'political_data.json')
	try:
		cwd = os.path.dirname(os.path.abspath(__file__))
		path = os.path.join(cwd, relative_path)
		return json.load(open(path))
	except:
		return json.loads(pkgutil.get_data('scattertext', relative_path).decode('utf-8'))


def make_category_text_iter():
	for speaker_obj in convention_speech_iter():
		political_party = speaker_obj['name']
		for speech in speaker_obj['speeches']:
			yield political_party, speech


def main():
	tdm = TermDocMatrixFactory(
		category_text_iter=make_category_text_iter(),
		clean_function=clean_function_factory(),
		nlp=fast_but_crap_nlp
	).build()
	j = 'function getDataAndInfo() { return ' + \
	    json.dumps((ScatterChart(tdm)
	                .to_dict('democrat',
	                         category_name='Democratic',
	                         not_category_name='Republican',
	                         transform=percentile_ordinal))) + ';}'
	open('demo/scripts/words.js', 'w').write(j)
	print('Open demo/scattertext.html in Chrome or Firefox.')


main()
