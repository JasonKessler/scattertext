import re

import scattertext as st
import spacy

nlp = spacy.blank('en')
nlp.add_pipe('sentencizer')

headline_df = st.SampleCorpora.GuardianHeadlines.get_data().assign(
    Parse=lambda df: df.Text.apply(nlp),
    MonthNum=lambda df: df.Date.apply(lambda x: x.month),
    Month=lambda df: df.Date.apply(lambda x: x.strftime("%B-%Y"))
)

corpus = st.CorpusFromParsedDocuments(
    headline_df,
    category_col='Month',
    parsed_col='Parse',
    feats_from_spacy_doc=st.FlexibleNGrams(
        ngram_sizes=[1, 2, 3]
    )
).build(
    show_progress=False
).compact(
    compactor=st.NPMICompactor(show_progress=False)
).get_stoplisted_corpus().filter_out(
    lambda x: re.match(r'^\W+$', x) is not None
).compact(
    compactor=st.AssociationCompactor(2000)
)

html = st.produce_scattertext_table(
    corpus=corpus,
    category_order=list(
        corpus.get_df()[['MonthNum', 'Month']].drop_duplicates().sort_values(by='MonthNum').Month
    ),
    all_category_scorer=st.AllCategoryTermScorer(corpus, term_scorer=st.BNSScorer),
    metadata = lambda c: c.get_df()['Date'].astype(str)
)

fn = 'demo_table.html'
with open(fn, 'w') as of:
    of.write(html)
print('open ./' + fn)
