from __future__ import print_function

import json
import os
import pkgutil
import re

from scattertext import TermDocMatrixFactory
from scattertext import produce_scattertext_html
from scattertext.FastButCrapNLP import fast_but_crap_nlp


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

def build_term_doc_matrix():
	term_doc_matrix = TermDocMatrixFactory(
		category_text_iter=iter_party_speech_pairs(),
		clean_function=clean_function_factory(),
		nlp=fast_but_crap_nlp
	).build()
	return term_doc_matrix


def main():
	term_doc_matrix = build_term_doc_matrix()
	html = produce_scattertext_html(term_doc_matrix,
	                                category='democrat',
	                                category_name='Democratic',
	                                not_category_name='Republican',
	                                width_in_pixels=1000)
	open('./demo.html', 'wb').write(html.encode('utf-8'))
	print('Open ./demo.html in Chrome or Firefox.')



if __name__ == '__main__':
	main()
