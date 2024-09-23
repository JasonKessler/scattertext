import numpy as np
import pandas as pd

from scattertext.Common import HALO_COLORS
from scattertext.semioticsquare.halo_utils import add_radial_parts_and_mag_to_term_coordinates
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference


class EmptyNeutralCategoriesError(Exception): pass


'''
!!! Need to properly segregate interfaces
'''

SEMIOTIC_SQUARE_TO_PART = {
    'b': 'top_left',
    'a': 'top_right',
    'a_and_b': 'top',
    'b_and_not_a': 'left',
    'a_and_not_b': 'right',
    'not_b': 'bottom_right',
    'not_a': 'bottom_left',
    'not_a_and_not_b': 'bottom',
}


class SemioticSquareBase(object):
    def get_labels(self):
        raise NotImplementedError()

    def get_axes(self, **kwargs):
        raise NotImplementedError()

    def get_lexicons(self, num_terms=10):
        raise NotImplementedError()


class SemioticSquare(SemioticSquareBase):
    '''
    Create a visualization of a semiotic square.  Requires Corpus to have
    at least three categories.
    >>> newsgroups_train = fetch_20newsgroups(subset='train',
    ...   remove=('headers', 'footers', 'quotes'))
    >>> vectorizer = CountVectorizer()
    >>> X = vectorizer.fit_transform(newsgroups_train.data)
    >>> corpus = st.CorpusFromScikit(
    ... 	X=X,
    ... 	y=newsgroups_train.target,
    ... 	feature_vocabulary=vectorizer.vocabulary_,
    ... 	category_names=newsgroups_train.target_names,
    ... 	raw_texts=newsgroups_train.data
    ... 	).build()
    >>> semseq = SemioticSquare(corpus,
    ... 	category_a = 'alt.atheism',
    ... 	category_b = 'soc.religion.christian',
    ... 	neutral_categories = ['talk.religion.misc']
    ... )
    >>> # A simple HTML table
    >>> html = SemioticSquareViz(semseq).to_html()
    >>> # The table with an interactive scatterplot below it
    >>> html = st.produce_semiotic_square_explorer(semiotic_square,
    ...                                            x_label='More Atheism, Less Xtnity',
    ...                                            y_label='General Religious Talk')
    '''

    def __init__(self,
                 term_doc_matrix,
                 category_a,
                 category_b,
                 neutral_categories,
                 labels=None,
                 term_ranker=AbsoluteFrequencyRanker,
                 scorer=None,
                 non_text=False):
        '''
        Parameters
        ----------
        term_doc_matrix : TermDocMatrix
            TermDocMatrix (or descendant) which will be used in constructing square.
        category_a : str
            Category name for term A
        category_b : str
            Category name for term B (in opposition to A)
        neutral_categories : list[str]
            List of category names that A and B will be contrasted to.  Should be in same domain.
        labels : dict
            None by default. Labels are dictionary of {'a_and_b': 'A and B', ...} to be shown
            above each category.
        term_ranker : TermRanker
            Class for returning a term-frequency convention_df
        scorer : termscoring class, optional
            Term scoring class for lexicon mining. Default: `scattertext.termscoring.ScaledFScore`
        non_text : bool, default False
            Use metadata/non-text
        '''
        assert category_a in term_doc_matrix.get_categories()
        assert category_b in term_doc_matrix.get_categories()
        for category in neutral_categories:
            assert category in term_doc_matrix.get_categories()
        if len(neutral_categories) == 0:
            raise EmptyNeutralCategoriesError()
        self.category_a_ = category_a
        self.category_b_ = category_b
        self.neutral_categories_ = neutral_categories
        self.non_text = non_text
        self._build_square(term_doc_matrix, term_ranker, labels, scorer)

    def _build_square(self, term_doc_matrix, term_ranker, labels, scorer):
        self.term_doc_matrix_ = term_doc_matrix
        self.term_ranker = term_ranker(term_doc_matrix).set_non_text(non_text=self.non_text)
        self.scorer = RankDifference() \
            if scorer is None else scorer
        self.axes = self._build_axes(scorer)
        self.lexicons = self._build_lexicons()
        self._labels = labels

    def get_axes(self, scorer=None):
        '''
        Returns
        -------
        pd.DataFrame
        '''
        if scorer:
            return self._build_axes(scorer)
        return self.axes

    def get_lexicons(self, num_terms=10):
        '''
        Parameters
        ----------
        num_terms, int

        Returns
        -------
        dict
        '''
        return {k: v.index[:num_terms]
                for k, v in self.lexicons.items()}

    def get_labels(self):
        a = self._get_default_a_label()
        b = self._get_default_b_label()
        default_labels = {'a': a,
                          'not_a': 'Not ' + a,
                          'b': b,
                          'not_b': 'Not ' + b,
                          'a_and_b': a + ' + ' + b,
                          'not_a_and_not_b': 'Not ' + a + ' + Not ' + b,
                          'a_and_not_b': a + ' + Not ' + b,
                          'b_and_not_a': 'Not ' + a + ' + ' + b}
        labels = self._labels
        if labels is None:
            labels = {}
        return {name + '_label': labels.get(name, default_labels[name])
                for name in default_labels}

    def _get_default_b_label(self):
        return self.category_b_

    def _get_default_a_label(self):
        return self.category_a_

    def _build_axes(self, scorer):
        if scorer is None:
            scorer = self.scorer
        tdf = self._get_term_doc_count_df()
        default_score = self.scorer.get_default_score()
        counts = tdf.sum(axis=1)
        tdf['x'] = self._get_x_axis(scorer, tdf)
        tdf.loc[np.isnan(tdf['x']), 'x'] = default_score
        tdf['y'] = self._get_y_axis(scorer, tdf)
        tdf.loc[np.isnan(tdf['y']), 'y'] = default_score
        tdf['counts'] = counts
        if default_score == 0.5:
            tdf['x'] = 2 * tdf['x'] - 1
            tdf['y'] = 2 * tdf['y'] - 1
        return tdf[['x', 'y', 'counts']]

    def _get_x_axis(self, scorer, tdf):
        return scorer.get_scores(
            tdf[self.category_a_ + ' freq'],
            tdf[self.category_b_ + ' freq']
        )

    def _get_y_axis(self, scorer, tdf):
        return scorer.get_scores(
            tdf[[t + ' freq' for t in [self.category_a_, self.category_b_]]].sum(axis=1),
            tdf[[t + ' freq' for t in self.neutral_categories_]].sum(axis=1)
        )

    def _get_term_doc_count_df(self):
        return (self.term_ranker.get_ranks()
        [[t + ' freq' for t in self._get_all_categories()]])

    def _get_all_categories(self):
        return [self.category_a_, self.category_b_] + self.neutral_categories_

    def _build_lexicons(self):
        axes_parts_df = add_radial_parts_and_mag_to_term_coordinates(term_coordinates_df=self.axes)
        self.axes['color'] = axes_parts_df.Part.apply(
            lambda x: HALO_COLORS.get(
                # can't figure out why this is needed, so don't change it until you do
                x.replace('left', 'RIGHT').replace('right', 'left').replace('RIGHT', 'right')
            )
        )
        self.lexicons = {
            semiotic_square_label: axes_parts_df[lambda df: df.Part == part].sort_values(by='Mag', ascending=False)
            for semiotic_square_label, part
            in SEMIOTIC_SQUARE_TO_PART.items()
        }
        return self.lexicons
