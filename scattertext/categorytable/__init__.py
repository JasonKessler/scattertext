import json
from bisect import bisect_left

import pandas as pd
import numpy as np
from scattertext.termranking import AbsoluteFrequencyRanker

from scattertext.termscoring.RankDifference import RankDifference
from scipy.stats import gmean
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression

from scattertext import Scalers
from scattertext.graphs.ComponentDiGraphHTMLRenderer import GraphRenderer
from scattertext.viz.HTMLSemioticSquareViz import ClickableTerms


class MultiCategoryAssociationBase:
    def __init__(self, corpus, use_metadata=False):
        self.corpus = corpus
        self.use_metadata = use_metadata

    def get_category_association(self):
        raise NotImplementedError()


class MultiCategoryAssociationScorer(MultiCategoryAssociationBase):
    def get_category_association(self, ranker=None, scorer=None):
        if scorer is None:
            scorer = RankDifference()
        if ranker is None:
            ranker = AbsoluteFrequencyRanker(self.corpus)
        if self.use_metadata:
            ranker = ranker.use_non_text_features()
        term_freq_df = ranker.get_ranks('')
        global_freq = term_freq_df.sum(axis=1)
        data = []
        for cat in self.corpus.get_categories():
            cat_freq = term_freq_df[cat]
            for term_rank, (term, score) in enumerate(scorer.get_scores(
                    cat_freq, global_freq - cat_freq
            ).sort_values(ascending=False).iteritems()):
                data.append({'Category': cat, 'Term': term, 'Rank': term_rank, 'Score': score})

        return pd.DataFrame(data).groupby('Rank')


class CategoryTableMaker(GraphRenderer):
    def __init__(self, corpus, num_rows=10, use_metadata=False):
        self.num_rows = num_rows
        self.corpus = corpus
        self.use_metadata = use_metadata
        self.rank_df = self._get_term_category_associations()

    def get_graph(self):


        table = '<div class="timelinecontainer"><table class="timelinetable">'
        table += '<tr><th>' + '</th><th>'.join(sorted(self.corpus.get_categories())) + '</th></tr>'
        min_font_size = 7
        max_font_size = 20
        display_df = self.rank_df[lambda df: df.Rank < self.num_rows]

        bin_boundaries = np.histogram_bin_edges(
            np.log(display_df.Frequency), bins=max_font_size - min_font_size
        )
        display_df['FontSize'] = display_df.Frequency.apply(np.log).apply(
            lambda x: bisect_left(bin_boundaries, x) + min_font_size
        )

        for rank, group_df in display_df.groupby('Rank'):
            table += '<tr><td class="clickabletd">' + '</td><td class="clickabletd">'.join([
                ClickableTerms.get_clickable_term(
                    row.Term,
                    style="font-size: " + str(row.FontSize)
                )
                for _, row in group_df.sort_values(by='Category').iterrows()
            ]) + '</td></tr>'
        table += '</table></div>'
        return table

    def get_javascript(self):
        d = {}
        for category, cat_df in self.rank_df.assign(Frequency=lambda df: df.Frequency.astype(int)).groupby('Category'):
            cat_d = {}
            for _, row in cat_df.iterrows():
                cat_d[row['Term']] = {'Rank': row['Rank'], 'Freq': row['Frequency']}
            d[category] = cat_d
        js = 'categoryFrequency = ' + json.dumps(d)  + ';\n\n'

        js += '''
        Array.from(document.querySelectorAll('.clickabletd')).map(
            function (node) {
                node.addEventListener('mouseenter', mouseEnterNode);
                node.addEventListener('mouseleave', mouseLeaveNode);
                node.addEventListener('click', clickNode);
            }
        )
        
        function clickNode() {
            //document.querySelectorAll(".dotgraph")
            //    .forEach(node => node.style.display = 'none');

            //var term = Array.prototype.filter
            //    .call(this.children, (x => x.tagName === "span"))[0].textContent;

            //plotInterface.handleSearchTerm(term, true);
            
            
        }

        function mouseEnterNode(event) {
            console.log("THIS"); console.log(this)
            var term = this.children[0].textContent;
            plotInterface.showTooltipSimple(term);
            var clickableTds = document.getElementsByClassName('clickabletd');
            for(var i = 0; i < clickableTds.length; i++) {
                var td = clickableTds[i];
                if(td.children[0].textContent == term) 
                    td.style.backgroundColor = "#FFAAAA";
            }
        }

        function mouseLeaveNode(event) {
            plotInterface.tooltip.transition().style('opacity', 0)
            var clickableTds = document.getElementsByClassName('clickabletd');            
            for(var i = 0; i < clickableTds.length; i++) 
                clickableTds[i].style.backgroundColor = "#FFFFFF";
        }'''
        return js

    def _get_term_category_associations(self):
        tdm = self.corpus.get_metadata_count_mat() if self.use_metadata else self.corpus.get_term_doc_mat()
        tdmtfidf = TfidfTransformer().fit_transform(tdm)
        coefs = np.zeros(shape=(self.corpus.get_num_categories(), tdm.shape[1]), dtype=float)
        for i, cat in enumerate(self.corpus.get_categories()):
            y = self.corpus.get_category_ids() == i
            clf = LogisticRegression(penalty='l2', C=5., max_iter=4000, tol=1e-6, solver='liblinear').fit(tdmtfidf, y)
            coefs[i, :] = clf.coef_
        coef_df = pd.DataFrame(
            coefs.T,
            index=self.corpus.get_terms(),
            columns=[x + ' coef' for x in self.corpus.get_categories()]
        )
        coef_freq_df = pd.merge(
            self.corpus.get_term_freq_df(),
            coef_df,
            left_index=True,
            right_index=True
        )
        for cat in self.corpus.get_categories():
            freq = Scalers.dense_rank(coef_freq_df[cat + ' freq'])
            coef = Scalers.scale_neg_1_to_1_with_zero_mean(coef_freq_df[cat + ' coef'])
            coef_freq_df[cat + ' gmean'] = gmean([freq, coef, coef])
        data = []
        for cat in self.corpus.get_categories():
            for term_rank, (term, row) in enumerate(
                    coef_freq_df[[
                        cat + ' gmean', cat + ' freq'
                    ]].sort_values(by=cat + ' gmean', ascending=False).iterrows()
            ):
                data.append({'Category': cat, 'Term': term, 'Rank': term_rank, 'Frequency': row[cat + ' freq']})
        return pd.DataFrame(data)
