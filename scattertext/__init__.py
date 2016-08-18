from __future__ import print_function

import json
import os
import pkgutil
import re

from scattertext import Scalers
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.IndexStore import IndexStore
from scattertext.ScatterChart import ScatterChart
from scattertext.TermDocMatrix import TermDocMatrix, InvalidScalerException
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory, FeatsFromDoc, TermDocMatrixFromPandas
from scattertext.TermDocMatrixFilter import TermDocMatrixFilter, filter_bigrams_by_pmis
from scattertext.FastButCrapNLP import fast_but_crap_nlp
import scattertext.viz

def convention_speech_iter():
	relative_path = os.path.join('data', 'political_data.json')
	try:
		cwd = os.path.dirname(os.path.abspath(__file__))
		path = os.path.join(cwd, relative_path)
		return json.load(path)
	except:
		return json.loads(pkgutil.get_data('scattertext', relative_path))


def iter_party_convention_speech(nlp=None):
	if nlp is None:
		from spacy.en import English
		nlp = English()
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

	for category_struct in convention_speech_iter():
		category_name = category_struct['name']
		print('category', category_struct['name'])
		print('# speeches', len(category_struct['speeches']))
		for speech_raw in category_struct['speeches']:
			clean_speech = only_speaker_text_re.sub('', speech_raw)
			parsed_speech = nlp(clean_speech)
			yield category_name, parsed_speech
