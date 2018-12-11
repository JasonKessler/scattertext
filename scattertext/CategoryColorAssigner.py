import pandas as pd

from scattertext.termscoring.RankDifference import RankDifference
from scattertext.Common import QUALITATIVE_COLORS
from scattertext.termranking import AbsoluteFrequencyRanker


class CategoryColorAssigner(object):
    def __init__(self,
                 corpus,
                 scorer=RankDifference(),
                 ranker=AbsoluteFrequencyRanker,
                 use_non_text_features=False,
                 color_palette=QUALITATIVE_COLORS):
        '''
        Assigns scores to colors for categories

        :param corpus: TermDocMatrix
        :param scorer: scorer
        :param color_palette: list of colors [[red, green, blue], ...]
        '''
        self.corpus = corpus
        self.scorer = scorer
        self.color_palette = color_palette
        my_ranker = ranker(corpus)
        if use_non_text_features:
            my_ranker.use_non_text_features()
        tdf = my_ranker.get_ranks()
        tdf_sum = tdf.sum(axis=1)
        term_scores = {}
        for cat in tdf.columns:
            term_scores[cat[:-5]] = pd.Series(self.scorer.get_scores(tdf[cat], tdf_sum - tdf[cat]), index=tdf.index)
        self.term_cat = pd.DataFrame(term_scores).idxmax(axis=1)
        ranked_list_categories = pd.Series(corpus.get_category_names_by_row()).value_counts().index
        self.category_colors = pd.Series(self.color_palette[:len(ranked_list_categories)],
                                         index=ranked_list_categories)

    def get_category_colors(self):
        return self.category_colors

    def get_term_colors(self):
        '''

        :return: dict, term -> color
        '''
        # print(self.category_colors)
        # print(self.term_cat)

        term_color = pd.Series(self.category_colors[self.term_cat].values, index=self.term_cat.index)

        def get_hex_color(color):
            return ''.join([part if len(part) == 2 else '0' + part
                            for part in [hex(part)[2:] for part in color]])

        return term_color.apply(get_hex_color).to_dict()