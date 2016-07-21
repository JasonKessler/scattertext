import json
import os
import re

import numpy as np
from spacy.en import English

from texttoideas import IndexStore
from texttoideas.CSRMatrixFactory import CSRMatrixFactory
from texttoideas.IndexStore import IndexStore
from texttoideas.TermDocMatrix import *

def convention_speech_iter():
	cwd = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(cwd, 'data', 'political_data.json')
	return json.load(open(path))


def iter_party_convention_speech(nlp=None,
                                 convention_speech_iter=convention_speech_iter):
	if nlp is None:
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

	for category_struct in convention_speech_iter:
		category_name = category_struct['name']
		print 'category', category_struct['name']
		print '# speeches', len(category_struct['speeches'])
		for speech_raw in category_struct['speeches']:
			clean_speech = only_speaker_text_re.sub('', speech_raw)
			parsed_speech = nlp(clean_speech)
			yield category_name, parsed_speech




def filter_bigrams_by_pmis(word_freq_df, threshold_coef=2):
	is_bigram = np.array([' ' in word for word in word_freq_df.index])
	unigram_freq = word_freq_df[~is_bigram].sum(axis=1)
	bigram_freq = word_freq_df[is_bigram].sum(axis=1)
	bigram_prob = bigram_freq / bigram_freq.sum()
	unigram_prob = unigram_freq / unigram_freq.sum()

	def get_pmi(bigram):
		return np.log(
			bigram_prob[bigram] / np.product([unigram_prob[word] for word in bigram.split(' ')])
		) / np.log(2)

	low_pmi_bigrams = bigram_prob[bigram_prob.index.map(get_pmi) < threshold_coef * 2]
	return word_freq_df.drop(low_pmi_bigrams.index)
