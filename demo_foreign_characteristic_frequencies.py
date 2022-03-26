import scattertext as st
import pandas as pd
import spacy

from zipfile import ZipFile
from urllib.request import urlopen
import re
import io

nlp = spacy.blank('pl')
nlp.add_pipe('sentencizer')


with ZipFile(io.BytesIO(urlopen(
    'https://klejbenchmark.com/static/data/klej_polemo2.0-in.zip'
).read())) as zf:
    train_df = pd.read_csv(zf.open('train.tsv'), sep='\t')[
        lambda df: df.target.isin(['__label__meta_plus_m', '__label__meta_minus_m'])
    ].assign(
        Parse = lambda df: df.sentence.apply(nlp)
    )

# Polish word frequencies from https://github.com/oprogramador/most-common-words-by-language
# This DataFrame needs to contain exactly two columns: 'word' and 'background', where word contains
# the text of the word, and background its frequency
polish_word_frequencies = pd.read_csv(
    'https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pl/pl_50k.txt',
    sep=' ',
    names=['Word', 'Frequency']
).set_index('Word')['Frequency']

polish_stopwords = {
    stopword for stopword in
    urlopen(
        'https://raw.githubusercontent.com/bieli/stopwords/master/polish.stopwords.txt'
    ).read().decode('utf-8').split('\n')
    if stopword.strip()
}

not_a_word = re.compile(r'^\W+$')

corpus = st.CorpusFromParsedDocuments(
    train_df,
    category_col='target',
    parsed_col='Parse'
).build(
).get_unigram_corpus(
).filter_out(
    lambda w: w in polish_stopwords or not_a_word.match(w) is not None
).set_background_corpus(
    polish_word_frequencies
).remove_infrequent_words(
    minimum_term_count=20
)

html = st.produce_scattertext_explorer(
    corpus,
    category='__label__meta_plus_m',
    category_name='Plus-M',
    not_category_name='Minus-M',
    minimum_term_frequency=1,
    width_in_pixels=1000,
    transform=st.Scalers.dense_rank
)

fn = 'demo_foreign_characteristic_frequencies.html'
open(fn, 'w').write(html)
print(f'Open ./{fn}')