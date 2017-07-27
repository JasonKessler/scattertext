import pandas as pd

# these are generated via _rebuild_suffixes
# valid emoji combos for spec 5.0
from scattertext.emojis.ProcessedEmojiStructure import VALID_EMOJIS


def _rebuild_suffixes(emoji_spec_url='http://www.unicode.org/Public/emoji/5.0/emoji-test.txt'):
	valid_seqs = (pd.DataFrame(pd.read_csv(emoji_spec_url,
	                                       sep=';', comment='#', names=['code_points', 'status'])
	['code_points'].apply(
		lambda x: pd.Series({'seq': [int(c, 16) for c in x.split()], 'len': len(x.split())})))
	              .sort_values(by=['len'], ascending=False)
	              ['seq'])
	suffixes_construct = {}
	for x in valid_seqs:
		suffix = tuple(x[1:])
		suffix_holder = suffixes_construct.setdefault(x[0], {})
		suffix_set = suffix_holder.setdefault(len(suffix), set())
		suffix_set.add(suffix)
	for k, v in suffixes_construct.items():
		suffixes_construct[k] = list(reversed(sorted(v.items())))
	return suffixes_construct

# some numbers and non-letter characters are slipping in
def _append_if_valid(found_emojis, candidate):
	for c in candidate:
		if ord(c) > 1000:
			found_emojis.append(candidate)
			return

def extract_emoji(text):
	'''
	Parameters
	----------
	text, str

	Returns
	-------
	List of 5.0-compliant emojis that occur in text.
	'''
	found_emojis = []
	len_text = len(text)
	i = 0
	while i < len_text:
		cur_char = ord(text[i])
		try:
			VALID_EMOJIS[cur_char]
		except:
			i += 1
			continue
		found = False
		for dict_len, candidates in VALID_EMOJIS[cur_char]:
			if i + dict_len <= len_text:
				if dict_len == 0:
					_append_if_valid(found_emojis,text[i])
					i += 1
					found = True
					break
				candidate = tuple(ord(c) for c in text[i + 1:i + 1 + dict_len])
				if candidate in candidates:
					_append_if_valid(found_emojis,text[i:i + 1 + dict_len])
					i += 1 + dict_len
					found = True
					break
			if found:
				break
		if not found:
			_append_if_valid(found_emojis,text[i])
			i += 1
	return found_emojis

