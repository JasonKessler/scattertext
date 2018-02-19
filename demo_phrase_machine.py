import spacy

from scattertext import SampleCorpora, whitespace_nlp_with_sentences, PhraseMachinePhrases
from scattertext import produce_scattertext_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.termcompaction.CompactTerms import CompactTerms

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          feats_from_spacy_doc=PhraseMachinePhrases(),
                          nlp=spacy.load('en', parser=False)).build()

compact_corpus = CompactTerms(corpus, minimum_term_count = 2).compact()
html = produce_scattertext_explorer(compact_corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    minimum_term_frequency=2,
                                    pmi_threshold_coefficient=0,
                                    width_in_pixels=1000,
                                    metadata=convention_df['speaker'])
open('./demo_phrase_machine.html', 'wb').write(html.encode('utf-8'))
print('Open ./demo_phrase_machine.html in Chrome or Firefox.')
