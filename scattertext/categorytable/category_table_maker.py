import json
from _bisect import bisect_left
from typing import Optional

import numpy as np
import pandas as pd

from scattertext.all_category_scorers.gmean_l2_freq_associator import AllCategoryScorerGMeanL2
from scattertext.all_category_scorers.all_category_scorer import AllCategoryScorer
from scattertext.graphs.ComponentDiGraphHTMLRenderer import GraphRenderer
from scattertext.viz.HTMLSemioticSquareViz import ClickableTerms


class CategoryTableMaker(GraphRenderer):
    def __init__(
            self,
            corpus,
            num_rows=10,
            use_metadata=False,
            category_order=None,
            all_category_scorer: Optional[AllCategoryScorer] = None,
            min_font_size=7,
            max_font_size=20
    ):
        self.num_rows = num_rows
        self.corpus = corpus
        self.use_metadata = use_metadata
        self.all_category_scorer_ = AllCategoryScorerGMeanL2(
            corpus=corpus,
            non_text=use_metadata
        ) if all_category_scorer is None else all_category_scorer
        self.rank_df = self._get_term_category_associations()
        self.category_order_ = (sorted(self.corpus.get_categories())
                                if category_order is None else category_order)
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size

    def get_graph(self):
        table = '<div class="timelinecontainer"><table class="timelinetable">'
        table += '<tr><th>' + '</th><th>'.join(self.category_order_) + '</th></tr>'
        display_df = self.__get_display_df()

        cat_df = self.__get_cat_df(display_df)

        for rank, group_df in display_df.groupby('Rank'):
            table += '<tr><td class="clickabletd">' + '</td><td class="clickabletd">'.join([
                ClickableTerms.get_clickable_term(
                    row.Term,
                    style="font-size: " + str(row.FontSize)
                )
                for _, row in group_df.sort_values(by='CategoryNum').iterrows()
            ]) + '</td></tr>'
        table += '<tr>' + ''.join([
            f'<td class="clickabletd" id="clickabletd-{row.CategoryNum}">&nbsp;</td>'
            for _, row in cat_df.iterrows()
        ]) + '</tr>' + '</table></div>'
        return table

    def __get_display_df(self):
        display_df = self.rank_df[lambda df: df.Rank < self.num_rows]
        bin_boundaries = np.histogram_bin_edges(
            np.log(display_df.Frequency), bins=self.max_font_size - self.min_font_size
        )
        display_df = pd.merge(
            display_df.assign(
                FontSize=lambda df: df.Frequency.apply(np.log).apply(
                    lambda x: bisect_left(bin_boundaries, x) + self.min_font_size
                )
            ),
            pd.DataFrame({
                'Category': self.category_order_,
                'CategoryNum': np.arange(len(self.category_order_))
            }),
            on='Category'
        )
        return display_df

    def __get_cat_df(self, display_df):
        cat_df = display_df[
            ['Category', 'CategoryNum']
        ].drop_duplicates().sort_values(by='CategoryNum')
        return cat_df

    def get_javascript(self):
        d = {}
        for category, cat_df in self.rank_df.assign(
                Frequency=lambda df: df.Frequency.astype(int)
        ).groupby('Category'):
            cat_d = {}
            for _, row in cat_df.iterrows():
                cat_d[row['Term']] = {'Rank': row['Rank'], 'Freq': row['Frequency']}
            d[category] = cat_d
        js = 'categoryFrequency = ' + json.dumps(d) + '; \n\n'
        cat_dict = dict(self.__get_cat_df(
            display_df=self.__get_display_df()
        ).set_index('Category')['CategoryNum'].astype(str))
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
                if(Object.entries(td.children).length > 0 && td.children[0].textContent == term) 
                    td.style.backgroundColor = "#FFAAAA";
                    
            }
            
            var termStats = []; 
            Object.keys(categoryFrequency).map(function(x) {
                termStats[x] = [
                    categoryFrequency[x][term]['Rank'], 
                    Object.values(categoryFrequency[x]).map(y=>y.Rank).reduce((a,b)=>Math.max(a,b), 0)
                ]
            });
            
            Object.entries(getCatNumToCat()).flatMap(
                function(kv) {
                    var td = document.getElementById('clickabletd-' + kv[1]);
                    var termStat = termStats[kv[0]];
                    if(termStat[0] >= ''' + str(self.num_rows) + ''') { 
                        td.style.tableLayout = 'fixed';
                        td.style.wordWrap = 'break-word';
                        td.style.backgroundColor = "#FFAAAA";
                        td.style.fontSize = "''' + str(self.min_font_size) + '''px";  
                        td.textContent = term + " (" + (termStat[0] + 1) + ")";
                    } else {
                        td.style.tableLayout = 'fixed';
                        td.style.wordWrap = 'break-word';
                        td.style.backgroundColor = "#FFFFFF";
                        td.style.fontSize = "''' + str(self.min_font_size) + '''px";  
                        td.textContent = "";
                    }
                }
            );
            
        }
        
        function mouseLeaveNode(event) {
            plotInterface.tooltip.transition().style('opacity', 0)
            var clickableTds = document.getElementsByClassName('clickabletd');            
            for(var i = 0; i < clickableTds.length; i++) 
                clickableTds[i].style.backgroundColor = "#FFFFFF";
                
            Object.entries(getCatNumToCat()).flatMap(
                function(kv) {
                    var td = document.getElementById('clickabletd-' + kv[1]);
                
                    td.style.tableLayout = 'fixed';
                    td.style.wordWrap = 'break-word';
                    td.style.backgroundColor = "#FFFFFF";
                    td.style.fontSize = "''' + str(self.min_font_size) + '''px";  
                    td.textContent = "";
                    
                }
            )                
        }
        
        function getCatNumToCat() { return ''' + json.dumps(cat_dict) + '''}'''
        return js

    def _get_term_category_associations(self) -> pd.DataFrame:
        return self.all_category_scorer_.get_rank_freq_df()
