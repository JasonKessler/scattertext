import spacy
from gensim.models import word2vec
from scattertext import whitespace_nlp_with_sentences
from scattertext import SampleCorpora, word_similarity_explorer_gensim, Word2VecFromParsedCorpus
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.termsignificance.ScaledFScoreSignificance import ScaledFScoreSignificance


def main():
	nlp = spacy.load('en')
	#nlp = whitespace_nlp_with_sentences
	convention_df = SampleCorpora.ConventionData2012.get_data()
	convention_df['parsed'] = convention_df.text.apply(nlp)
	corpus = (CorpusFromParsedDocuments(convention_df,
	                                   category_col='party',
	                                   parsed_col='parsed')
	          .build()
	          .get_unigram_corpus())
	model = word2vec.Word2Vec(size=100,
	                          alpha=0.025,
	                          window=5,
	                          min_count=5,
	                          max_vocab_size=None,
	                          sample=0,
	                          seed=1,
	                          workers=1,
	                          min_alpha=0.0001,
	                          sg=1,
	                          hs=1,
	                          negative=0,
	                          cbow_mean=0,
	                          iter=10,
	                          null_word=0,
	                          trim_rule=None,
	                          sorted_vocab=1)
	html = word_similarity_explorer_gensim(corpus,
	                                       category='democrat',
	                                       target_term='jobs',
	                                       category_name='Democratic',
	                                       not_category_name='Republican',
	                                       minimum_term_frequency=5,
	                                       width_in_pixels=1000,
	                                       metadata=convention_df['speaker'],
	                                       word2vec=Word2VecFromParsedCorpus(corpus, model).train(),
	                                       term_significance=ScaledFScoreSignificance(),
	                                       max_p_val=0.05,
	                                       save_svg_button=True,
	                                       d3_url='scattertext/data/viz/scripts/d3.min.js',
	                                       d3_scale_chromatic_url='scattertext/data/viz/scripts/d3-scale-chromatic.v1.min.js')
	open('./demo_gensim_similarity.html', 'wb').write(html.encode('utf-8'))
	print('Open ./demo_gensim_similarity.html in Chrome or Firefox.')


if __name__ == '__main__':
	main()
