import re

import scattertext as st
import spacy

#nlp = spacy.load('en_core_web_sm')
nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

headline_df = st.SampleCorpora.GuardianHeadlines.get_data().assign(
    Parse=lambda df: df.Text.progress_apply(nlp),
    MonthNum=lambda df: df.Date.apply(lambda x: x.month),
    Month=lambda df: df.Date.apply(lambda x: x.strftime("%B-%Y")),
    DateStr=lambda df: df.Date.apply(lambda x: x.strftime("%Y-%m-%d")),
)

word_number_matcher = re.compile('^[A-Za-z0-9 ]+$')

def exclude_ngrams_which_do_not_start_and_end_with_function_words(ngram: spacy.tokens.Span) -> bool:
    return any([ngram[0].orth_ in st.MY_ENGLISH_STOP_WORDS,
                ngram[-1].orth_ in st.MY_ENGLISH_STOP_WORDS,
                word_number_matcher.match(ngram[0].orth_.strip()) is None,
                word_number_matcher.match(ngram[-1].orth_.strip()) is None])

corpus = st.OffsetCorpusFactory(
    headline_df,
    category_col='DateStr',
    parsed_col='Parse',
    feat_and_offset_getter=st.FlexibleNGramFeatures(
        ngram_sizes=[1, 2, 3, 4, 5],
        exclude_ngram_filter = exclude_ngrams_which_do_not_start_and_end_with_function_words
    )
).build().compact(
    compactor=st.NPMICompactor(
        minimum_term_count = 3,
        number_terms_per_length = 2000,
    ),
    non_text=True
).compact(
    st.NgramPercentageCompactor(
        usage_portion=0.6,
    ),
    non_text=True
).filter_out(
    lambda x: len(x) == 1,
    non_text=True
).compact(
    compactor=st.AssociationCompactor(
        2000,
        scorer=st.DeltaJSDivergenceScorer,
        term_ranker=st.OncePerDocFrequencyRanker,
        use_non_text_features=True,
    ),
    non_text=True
)

html = st.produce_scattertext_table(
    corpus=corpus,
    category_order=list(sorted(corpus.get_categories())),
    all_category_scorer=st.AllCategoryTermScorer(corpus, term_scorer=st.LogLikelihoodRatio),
    metadata = lambda c: c.get_df()['Date'].astype(str),
    ignore_categories=False,
    plot_width=1000,
    sort_doc_labels_by_name=True,
    use_offsets=True,
    non_text=True,
)

fn = 'demo_table.html'
with open(fn, 'w') as of:
    of.write(html)
print('open ./' + fn)
