from __future__ import print_function

from urllib.request import urlopen

import pandas as pd

from scattertext import CorpusFromParsedDocuments
from scattertext import japanese_nlp
from scattertext import produce_scattertext_explorer
# compare chinese translations of tale of two cities and ulysses, from http://www.pku.edu.cn/study/novel/ulysses/cindex.htm

def main():
	#df = pd.read_csv('https://cdn.rawgit.com/JasonKessler/scattertext/e508bf32/scattertext/data/chinese.csv')
	shisei = _parse_geutenberg('http://www.gutenberg.org/files/31617/31617-0.txt')
	horadanshaku = _parse_geutenberg('http://www.gutenberg.org/files/34084/34084-0.txt')
	df = pd.DataFrame({'text': [shisei, horadanshaku],
	                   'title': ['Shisei', 'Horadanshaku tabimiyage'],
	                   'author': ['Akutagawa Ryunosuke', 'Kuni Sasaki']})

	df['text'] = df['text'].apply(japanese_nlp)
	corpus = CorpusFromParsedDocuments(df,
	                                   category_col='title',
	                                   parsed_col='text').build()
	html = produce_scattertext_explorer(corpus,
	                                    category='Shisei',
	                                    category_name='Shisei',
	                                    not_category_name='Horadanshaku tabimiyage',
	                                    minimum_term_frequency=5,
	                                    width_in_pixels=1000,
	                                    metadata=df['title'] + ' by ' + df['author'],
	                                    asian_mode=True)
	open('./demo_japanese.html', 'w').write(html)
	print('Open ./demo_japanese.html in Chrome or Firefox.')


def _parse_geutenberg(url):
	return (urlopen(url)
	        .read()
	        .decode('utf-8')
	        .split("Transcriber's Notes")[0]
	        .split('-------------------------------------------------------')[-1])


if __name__ == '__main__':
	main()
