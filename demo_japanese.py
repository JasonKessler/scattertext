import pandas as pd
from urllib.request import urlopen
import scattertext as st

def main():
	shisei = _parse_geutenberg('http://www.gutenberg.org/files/31617/31617-0.txt')
	horadanshaku = _parse_geutenberg('http://www.gutenberg.org/files/34084/34084-0.txt')
	df = pd.DataFrame({'text': [shisei, horadanshaku],
	                   'title': ['Shisei', 'Horadanshaku tabimiyage'],
	                   'author': ['Akutagawa Ryunosuke', 'Kuni Sasaki']})

	df['text'] = df['text'].apply(st.japanese_nlp)
	corpus = st.CorpusFromParsedDocuments(df,
	                                      category_col='title',
	                                      parsed_col='text').build()
	html = st.produce_scattertext_explorer(corpus,
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
