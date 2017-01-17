from __future__ import print_function

import pandas as pd

from scattertext import CorpusFromParsedDocuments
from scattertext import chinese_nlp
from scattertext import produce_scattertext_explorer
# compare chinese translations of tale of two cities and ulysses, from http://www.pku.edu.cn/study/novel/ulysses/cindex.htm

def main():
	df = pd.read_csv('https://cdn.rawgit.com/JasonKessler/scattertext/e508bf32/scattertext/data/chinese.csv')
	df['text'] = df['text'].apply(chinese_nlp)
	corpus = CorpusFromParsedDocuments(df,
	                                   category_col='novel',
	                                   parsed_col='text').build()
	html = produce_scattertext_explorer(corpus,
	                                    category='Tale of Two Cities',
	                                    category_name='Tale of Two Cities',
	                                    not_category_name='Ulysses',
	                                    width_in_pixels=1000,
	                                    metadata=df['novel'],
	                                    chinese_mode=True)
	open('./demo_chinese.html', 'w').write(html)
	print('Open ./demo_chinese.html in Chrome or Firefox.')


if __name__ == '__main__':
	main()
