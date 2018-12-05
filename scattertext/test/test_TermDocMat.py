import os
import pkgutil
from unittest import TestCase

import numpy as np
import pandas as pd
from scattertext.indexstore import IndexStore
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.linear_model import LinearRegression

from scattertext import TermDocMatrixFromPandas, CompactTerms, CSRMatrixFactory
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.TermDocMatrix import TermDocMatrix, SPACY_ENTITY_TAGS, \
    CannotCreateATermDocMatrixWithASignleCategoryException
from scattertext.TermDocMatrixFactory import build_from_category_whitespace_delimited_text
from scattertext.WhitespaceNLP import whitespace_nlp
from scattertext.termscoring.ScaledFScore import InvalidScalerException
from scattertext.test.test_corpusFromPandas import get_docs_categories
from scattertext.test.test_semioticSquare import get_docs_categories_semiotic
from scattertext.test.test_termDocMatrixFactory import build_hamlet_jz_corpus_with_meta


def make_a_test_term_doc_matrix():
    # type: () -> TermDocMatrix
    return build_from_category_whitespace_delimited_text(
        get_test_categories_and_documents()
    )


def get_test_categories_and_documents():
    return [
        ['a', '''hello my name is joe.
			i've got a wife and three kids and i'm working.
			in a button factory'''],
        ['b', '''this is another type of document
			 another sentence in another document
			 my name isn't joe here.'''],
        ['b', '''this is another document.
				blah blah blah''']
    ]


class TestTermDocMat(TestCase):
    @classmethod
    def setUp(cls):
        cls.tdm = make_a_test_term_doc_matrix()

    def test_get_num_terms(self):
        self.assertEqual(self.tdm.get_num_terms(), self.tdm._X.shape[1])

    def test_get_term_freq_df(self):
        df = self.tdm.get_term_freq_df().sort_values('b freq', ascending=False)[:3]
        self.assertEqual(list(df.index), ['another', 'blah', 'blah blah'])
        self.assertEqual(list(df['a freq']), [0, 0, 0])
        self.assertEqual(list(df['b freq']), [4, 3, 2])
        self.assertEqual(list(self.tdm.get_term_freq_df()
                              .sort_values('a freq', ascending=False)
                              [:3]['a freq']),
                         [2, 2, 1])

    def test_single_category_term_doc_matrix_should_error(self):
        with self.assertRaisesRegex(
                expected_exception=CannotCreateATermDocMatrixWithASignleCategoryException,
                expected_regex='Documents must be labeled with more than one category. '
                               'All documents were labeled with category: "a"'):
            single_category_tdm = build_from_category_whitespace_delimited_text(
                [['a', text]
                 for category, text
                 in get_test_categories_and_documents()]
            )

    def test_total_unigram_count(self):
        self.assertEqual(self.tdm.get_total_unigram_count(), 36)

    def test_get_term_df(self):
        categories, documents = get_docs_categories()
        df = pd.DataFrame({'category': categories,
                           'text': documents})
        tdm_factory = TermDocMatrixFromPandas(df,
                                              'category',
                                              'text',
                                              nlp=whitespace_nlp)
        term_doc_matrix = tdm_factory.build()

        term_df = term_doc_matrix.get_term_freq_df()
        self.assertEqual(dict(term_df.ix['speak up']),
                         {'??? freq': 2, 'hamlet freq': 0, 'jay-z/r. kelly freq': 1})
        self.assertEqual(dict(term_df.ix['that']),
                         {'??? freq': 0, 'hamlet freq': 2, 'jay-z/r. kelly freq': 0})

    def test_get_terms(self):
        tdm = make_a_test_term_doc_matrix()

        self.assertEqual(tdm.get_terms(),
                         ['hello', 'my', 'name', 'is', 'joe.', 'hello my', 'my name', 'name is', 'is joe.', "i've",
                          'got',
                          'a', 'wife', 'and', 'three', 'kids', "i'm", 'working.', "i've got", 'got a', 'a wife',
                          'wife and',
                          'and three', 'three kids', 'kids and', "and i'm", "i'm working.", 'in', 'button', 'factory',
                          'in a', 'a button', 'button factory', 'this', 'another', 'type', 'of', 'document', 'this is',
                          'is another', 'another type', 'type of', 'of document', 'sentence', 'another sentence',
                          'sentence in', 'in another', 'another document', "isn't", 'joe', 'here', "name isn't",
                          "isn't joe", 'joe here', 'document.', 'another document.', 'blah', 'blah blah']
                         )

    def test_get_unigram_corpus(self):
        tdm = make_a_test_term_doc_matrix()
        uni_tdm = tdm.get_unigram_corpus()
        term_df = tdm.get_term_freq_df()
        uni_term_df = uni_tdm.get_term_freq_df()
        self.assertEqual(set(term for term in term_df.index if ' ' not in term and "'" not in term),
                         set(uni_term_df.index))

    def test_remove_entity_tags(self):
        tdm = make_a_test_term_doc_matrix()
        removed_tags_tdm = tdm.remove_entity_tags()
        term_df = tdm.get_term_freq_df()
        removed_tags_term_df = removed_tags_tdm.get_term_freq_df()
        expected_terms = set(term for term in term_df.index
                             if not any(t in SPACY_ENTITY_TAGS for t in term.split()))
        removed_terms = set(removed_tags_term_df.index)
        self.assertEqual(expected_terms, removed_terms),

    def test_get_stoplisted_unigram_corpus(self):
        tdm = make_a_test_term_doc_matrix()
        uni_tdm = tdm.get_stoplisted_unigram_corpus()
        term_df = tdm.get_term_freq_df()
        uni_term_df = uni_tdm.get_term_freq_df()
        self.assertEqual(set(term for term in term_df.index
                             if ' ' not in term
                             and "'" not in term
                             and term not in ENGLISH_STOP_WORDS),
                         set(uni_term_df.index)),

    def test_get_stoplisted_unigram_corpus_and_custom(self):
        tdm = make_a_test_term_doc_matrix()
        uni_tdm = tdm.get_stoplisted_unigram_corpus_and_custom(['joe'])
        self._assert_stoplisted_minus_joe(tdm, uni_tdm)

        uni_tdm = tdm.get_stoplisted_unigram_corpus_and_custom('joe')
        self._assert_stoplisted_minus_joe(tdm, uni_tdm)

    def _assert_stoplisted_minus_joe(self, tdm, uni_tdm):
        term_df = tdm.get_term_freq_df()
        uni_term_df = uni_tdm.get_term_freq_df()
        self.assertEqual(set(term for term in term_df.index
                             if ' ' not in term
                             and 'joe' != term.lower()
                             and "'" not in term
                             and term not in ENGLISH_STOP_WORDS),
                         set(uni_term_df.index)),

    def test_term_doc_lists(self):
        term_doc_lists = self.tdm.term_doc_lists()
        self.assertEqual(type(term_doc_lists), dict)
        self.assertEqual(term_doc_lists['this'], [1, 2])
        self.assertEqual(term_doc_lists['another document'], [1])
        self.assertEqual(term_doc_lists['is'], [0, 1, 2])

    def test_remove_terms(self):
        tdm = make_a_test_term_doc_matrix()
        with self.assertRaises(KeyError):
            tdm.remove_terms(['elephant'])
        tdm_removed = tdm.remove_terms(['hello', 'this', 'is'])
        removed_df = tdm_removed.get_term_freq_df()
        df = tdm.get_term_freq_df()
        self.assertEqual(tdm_removed.get_num_docs(), tdm.get_num_docs())
        self.assertEqual(len(removed_df), len(df) - 3)
        self.assertNotIn('hello', removed_df.index)
        self.assertIn('hello', df.index)

    def test_remove_terms_used_less_than_num_docs(self):
        tdm = make_a_test_term_doc_matrix()
        tdm2 = tdm.remove_terms_used_in_less_than_num_docs(2)
        self.assertTrue(all(tdm2.get_term_freq_df().sum(axis=1) >= 2))

    def test_term_scores(self):
        df = self.tdm.get_term_freq_df()
        df['posterior ratio'] = self.tdm.get_posterior_mean_ratio_scores('b')
        scores = self.tdm.get_scaled_f_scores('b', scaler_algo='percentile')
        df['scaled_f_score'] = np.array(scores)
        with self.assertRaises(InvalidScalerException):
            self.tdm.get_scaled_f_scores('a', scaler_algo='x')
        self.tdm.get_scaled_f_scores('a', scaler_algo='percentile')
        self.tdm.get_scaled_f_scores('a', scaler_algo='normcdf')
        df['rudder'] = self.tdm.get_rudder_scores('b')
        df['corner'] = self.tdm.get_corner_scores('b')
        df['fisher oddsratio'], df['fisher pval'] = self.tdm.get_fisher_scores('b')

        self.assertEqual(list(df.sort_values(by='posterior ratio', ascending=False).index[:3]),
                         ['another', 'blah', 'blah blah'])
        self.assertEqual(list(df.sort_values(by='scaled_f_score', ascending=False).index[:3]),
                         ['another', 'blah', 'blah blah'])

        # to do: come up with faster way of testing fisher
        # self.assertEqual(list(convention_df.sort_values(by='fisher pval', ascending=True).index[:3]),
        #                 ['another', 'blah', 'blah blah'])

        self.assertEqual(list(df.sort_values(by='rudder', ascending=True).index[:3]),
                         ['another', 'blah', 'blah blah'])

    def test_term_scores_background(self):
        hamlet = get_hamlet_term_doc_matrix()
        df = hamlet.get_scaled_f_scores_vs_background(
            scaler_algo='none'
        )
        self.assertEqual({u'corpus', u'background', u'Scaled f-score'},
                         set(df.columns))
        self.assertEqual(list(df.index[:3]),
                         ['polonius', 'laertes', 'osric'])

        df = hamlet.get_rudder_scores_vs_background()
        self.assertEqual({u'corpus', u'background', u'Rudder'},
                         set(df.columns))
        self.assertEqual(list(df.index[:3]),
                         ['voltimand', 'knavish', 'mobled'])

        df = hamlet.get_posterior_mean_ratio_scores_vs_background()
        self.assertEqual({u'corpus', u'background', u'Log Posterior Mean Ratio'},
                         set(df.columns))
        self.assertEqual(list(df.index[:3]),
                         ['hamlet', 'horatio', 'claudius'])

    def test_keep_only_these_categories(self):
        df = pd.DataFrame(data=pd.np.array(get_docs_categories_semiotic()).T,
                          columns=['category', 'text'])
        corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
        hamlet_swift_corpus = corpus.keep_only_these_categories(['hamlet', 'swift'])
        self.assertEqual(hamlet_swift_corpus.get_categories(), ['hamlet', 'swift'])
        self.assertGreater(len(corpus.get_terms()), len(hamlet_swift_corpus.get_terms()))
        with self.assertRaises(AssertionError):
            corpus.keep_only_these_categories(['hamlet', 'swift', 'asdjklasfd'])
        corpus.keep_only_these_categories(['hamlet', 'swift', 'asdjklasfd'], True)

    def test_remove_categories(self):
        df = pd.DataFrame(data=pd.np.array(get_docs_categories_semiotic()).T,
                          columns=['category', 'text'])
        corpus = CorpusFromPandas(df, 'category', 'text', nlp=whitespace_nlp).build()
        swiftless = corpus.remove_categories(['swift'])

        swiftless_constructed = CorpusFromPandas(df[df['category'] != 'swift'],
                                                 'category',
                                                 'text',
                                                 nlp=whitespace_nlp).build()
        np.testing.assert_equal(
            [i for i in corpus._y if i != corpus.get_categories().index('swift')],
            swiftless._y
        )
        self.assertEqual(swiftless._y.shape[0], swiftless._X.shape[0])
        self.assertEqual(swiftless_constructed._X.shape, swiftless._X.shape)
        self.assertEqual(set(swiftless_constructed.get_terms()),
                         set(swiftless.get_terms()))
        pd.testing.assert_series_equal(swiftless_constructed.get_texts(),
                                       swiftless.get_texts())

    def test_get_category_names_by_row(self):
        hamlet = get_hamlet_term_doc_matrix()
        returned = hamlet.get_category_names_by_row()
        self.assertEqual(len(hamlet._y),
                         len(returned))
        np.testing.assert_almost_equal([hamlet.get_categories().index(x)
                                        for x in returned],
                                       hamlet._y)

    def test_set_background_corpus(self):
        tdm = get_hamlet_term_doc_matrix()
        with self.assertRaisesRegex(Exception, "The argument.+"):
            tdm.set_background_corpus(1)
        with self.assertRaisesRegex(Exception, "The argument.+"):
            back_df = pd.DataFrame()
            tdm.set_background_corpus(back_df)
        with self.assertRaisesRegex(Exception, "The argument.+"):
            back_df = pd.DataFrame({'word': ['a', 'bee'], 'backgasdround': [3, 1]})
            tdm.set_background_corpus(back_df)
        back_df = pd.DataFrame({'word': ['a', 'bee'], 'background': [3, 1]})
        tdm.set_background_corpus(back_df)
        tdm.set_background_corpus(tdm)

    def test_compact(self):
        x = get_hamlet_term_doc_matrix().compact(CompactTerms(minimum_term_count=3))
        self.assertEqual(type(x), TermDocMatrix)

    def test_get_background_corpus(self):
        tdm = get_hamlet_term_doc_matrix()
        # background = tdm.get_background_corpus()
        # self.assertEqual(background, None)
        back_df = pd.DataFrame({'word': ['a', 'bee'], 'background': [3, 1]})
        tdm.set_background_corpus(back_df)
        self.assertEqual(tdm.get_background_corpus().to_dict(),
                         back_df.to_dict())
        tdm.set_background_corpus(tdm)
        self.assertEqual(set(tdm.get_background_corpus().to_dict().keys()),
                         set(['word', 'background']))

    # to do: come up with faster way of testing fisher
    # convention_df = hamlet.get_fisher_scores_vs_background()
    # self.assertEqual(list(convention_df.sort_values(by='Bonferroni-corrected p-values', ascending=True).index[:3]),
    #                 ['voltimand', 'knavish', 'mobled'])

    def test_log_reg(self):
        hamlet = get_hamlet_term_doc_matrix()
        df = hamlet.get_term_freq_df()
        df['logreg'], acc, baseline = hamlet.get_logistic_regression_coefs_l2('hamlet', clf=LinearRegression())
        l1scores, acc, baseline = hamlet.get_logistic_regression_coefs_l1('hamlet', clf=LinearRegression())
        self.assertGreaterEqual(acc, 0)
        self.assertGreaterEqual(baseline, 0)
        self.assertGreaterEqual(1, acc)
        self.assertGreaterEqual(1, baseline)
        self.assertEqual(list(df.sort_values(by='logreg', ascending=False).index[:3]),
                         ['the', 'starts', 'incorporal'])

    def test_get_doc_lengths(self):
        hamlet = get_hamlet_term_doc_matrix()
        hamlet_unigram = hamlet.get_unigram_corpus()
        self.assertEqual(len(hamlet.get_doc_lengths()), hamlet.get_num_docs())
        np.testing.assert_array_equal(hamlet.get_doc_lengths(), hamlet_unigram._X.sum(axis=1).A1)

    def test_get_category_ids(self):
        hamlet = get_hamlet_term_doc_matrix()
        np.testing.assert_array_equal(hamlet.get_category_ids(), hamlet._y)

    def test_add_metadata(self):
        hamlet = get_hamlet_term_doc_matrix()
        meta_index_store = IndexStore()
        meta_fact = CSRMatrixFactory()
        for i in range(hamlet.get_num_docs()):
            meta_fact[i, i] = meta_index_store.getidx(str(i))
        other_hamlet = hamlet.add_metadata(meta_fact.get_csr_matrix(),
                                           meta_index_store)
        assert other_hamlet == hamlet
        meta_index_store = IndexStore()
        meta_fact = CSRMatrixFactory()
        for i in range(hamlet.get_num_docs() - 5):
            meta_fact[i, i] = meta_index_store.getidx(str(i))
        with self.assertRaises(AssertionError):
            hamlet.add_metadata(meta_fact.get_csr_matrix(),
                                meta_index_store)

    def test_metadata_in_use(self):
        hamlet = get_hamlet_term_doc_matrix()
        self.assertFalse(hamlet.metadata_in_use())
        hamlet_meta = build_hamlet_jz_corpus_with_meta()
        self.assertTrue(hamlet_meta.metadata_in_use())

    def test_get_term_doc_mat(self):
        hamlet = get_hamlet_term_doc_matrix()
        X = hamlet.get_term_doc_mat()
        np.testing.assert_array_equal(X.shape, (hamlet.get_num_docs(), hamlet.get_num_terms()))

    def test_get_metadata_doc_mat(self):
        hamlet_meta = build_hamlet_jz_corpus_with_meta()
        mX = hamlet_meta.get_metadata_doc_mat()
        np.testing.assert_array_equal(mX.shape, (hamlet_meta.get_num_docs(), len(hamlet_meta.get_metadata_freq_df())))

    def test_get_metadata(self):
        hamlet_meta = build_hamlet_jz_corpus_with_meta()
        self.assertEqual(hamlet_meta.get_metadata(), ['cat1'])

    def test_get_category_index_store(self):
        hamlet = get_hamlet_term_doc_matrix()
        idxstore = hamlet.get_category_index_store()
        self.assertIsInstance(idxstore, IndexStore)
        self.assertEquals(idxstore.getvals(), {'hamlet', 'not hamlet'})

    def test_recategorize(self):
        hamlet = get_hamlet_term_doc_matrix()
        newcats = ['cat' + str(i % 3) for i in range(hamlet.get_num_docs())]
        newhamlet = hamlet.recategorize(newcats)
        self.assertEquals(set(newhamlet.get_term_freq_df('').columns),
                          {'cat0', 'cat1', 'cat2'})
        self.assertEquals(set(hamlet.get_term_freq_df('').columns),
                          {'hamlet', 'not hamlet'})


def get_hamlet_term_doc_matrix():
    # type: () -> TermDocMatrix
    hamlet_docs = get_hamlet_docs()

    hamlet_term_doc_matrix = build_from_category_whitespace_delimited_text(
        [(get_hamlet_snippet_binary_category(text), text)
         for i, text in enumerate(hamlet_docs)]
    )
    return hamlet_term_doc_matrix


def get_hamlet_snippet_binary_category(text):
    return 'hamlet' if 'hamlet' in text.lower() else 'not hamlet'


def get_hamlet_docs():
    try:
        cwd = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(cwd, '..', 'data', 'hamlet.txt')
        buf = open(path).read()
    except:
        buf = pkgutil.get_data('scattertext', os.path.join('data', 'hamlet.txt'))
    hamlet_docs = buf.split('\n\n')
    return hamlet_docs
