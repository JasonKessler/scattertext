from __future__ import print_function

import os
import pkgutil
import re

import pandas as pd
import json

from scattertext import CorpusFromParsedDocuments, produce_scattertext_explorer
from scattertext.WhitespaceNLP import whitespace_nlp


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


def iter_party_speech_pairs():
	for speaker_obj in convention_speech_iter():
		political_party = speaker_obj['name']
		for speech in speaker_obj['speeches']:
			yield political_party, speech


def speaker_function_factory():
	only_speaker_text_re = re.compile(
		r'((^|\n)((ANNOUNCER|AUDIENCE MEMBERS?): .+)($|\n)|(\n|^)(((?P<name>[A-Z\.()\- ]+): ))|\(.+\) *)',
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


def speaker_name_factory():
	name_re = re.compile(r'.*(\n|^)(?P<name>[A-Z0-9 ]+):\w*.+', re.M)

	def speaker_name(text):
		for _, name in name_re.findall(text):
			if name not in ('ANNOUNCER', 'AUDIENCE MEMBER', 'AUDIENCE MEMBERS'):
				return name

	return speaker_name


def make_political_corpus():
	clean = clean_function_factory()
	get_speaker_name = speaker_name_factory()
	data = []
	for party, speech in iter_party_speech_pairs():
		cleaned_speech = clean(speech)
		speaker_name = get_speaker_name(speech)
		if cleaned_speech and cleaned_speech != '' and speaker_name != '':
			parsed_speech = whitespace_nlp(cleaned_speech)
			data.append({'party': party,
			             'text': parsed_speech,
			             'speaker': speaker_name})
	source_df = pd.DataFrame(data)
	corpus = CorpusFromParsedDocuments(source_df,
	                                   category_col='party',
	                                   parsed_col='text').build()
	return corpus, source_df


def main():
	corpus, source_df = make_political_corpus()
	html = produce_scattertext_explorer(corpus,
	                                    category='democrat',
	                                    category_name='Democratic',
	                                    not_category_name='Republican',
	                                    width_in_pixels=1000,
	                                    metadata=source_df['speaker'],
	                                    )
	open('./demo.html', 'wb').write(html.encode('utf-8'))
	print('Open ./demo.html in Chrome or Firefox.')


if __name__ == '__main__':
	main()
