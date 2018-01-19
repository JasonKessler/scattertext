from scattertext import SampleCorpora, produce_fightin_words_explorer
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.WhitespaceNLP import whitespace_nlp_with_sentences
from scattertext.termsignificance.LogOddsRatioInformativeDirichletPiror import LogOddsRatioInformativeDirichletPrior

convention_df = SampleCorpora.ConventionData2012.get_data()
corpus = CorpusFromPandas(convention_df,
                          category_col='party',
                          text_col='text',
                          nlp=whitespace_nlp_with_sentences).build()
'''
term_freq_df = corpus.get_term_freq_df()
frequencies_scaled = scale(np.log(term_freq_df.sum(axis=1).values))
zeta_i_j = (LogOddsRatioUninformativeDirichletPrior()
	.get_zeta_i_j_given_separate_counts(term_freq_df['democrat freq'],
                                      term_freq_df['republican freq']))
zeta_scaled_for_charting = scale_neg_1_to_1_with_zero_mean_abs_max(zeta_i_j)

html = produce_scattertext_explorer(corpus,
                                    category='democrat',
                                    category_name='Democratic',
                                    not_category_name='Republican',
                                    minimum_term_frequency=5,
                                    width_in_pixels=1000,
                                    x_coords=frequencies_scaled,
                                    y_coords=zeta_scaled_for_charting,
                                    scores=zeta_i_j,
                                    sort_by_dist=False,
                                    metadata=convention_df['speaker'],
                                    x_label='Log Frequency',
                                    y_label='Log Odds Ratio w/ Prior (a_w=0.01)')
'''

bg_df = (corpus
	.get_term_and_background_counts()
	.where(lambda x: x.corpus > 0).dropna()
)
bg_df.background += bg_df.corpus
corpus_bg = corpus.remove_terms(set(corpus.get_terms()) - set(bg_df.index))
priors = (corpus_bg
	.get_term_and_background_counts()
	.reindex(corpus_bg.get_terms())['background']
)
term_scorer = LogOddsRatioInformativeDirichletPrior(priors.values, 10)


tooltip_context = '''(function(d) {
	return d.term+"<br/>Count ratio (per 25k): "+d.cat25k+":"+d.ncat25k+"<br/>Z-score: "+ Number(Math.round(d.os+'e3')+'e-3');
})'''

html = produce_fightin_words_explorer(corpus_bg,
                                      category='democrat',
                                      category_name='Democratic',
                                      not_category_name='Republican',
                                      minimum_term_frequency=5,
                                      get_tooltip_content = tooltip_context,
                                      term_scorer=term_scorer)

file_name = 'demo_log_odds_ratio_prior_10.html'
open(file_name, 'wb').write(html.encode('utf-8'))
print('Open %s in Chrome or Firefox.' % file_name)
