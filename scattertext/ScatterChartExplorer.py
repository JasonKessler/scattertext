import numpy as np

from scattertext import ScatterChart, TermCategoryFrequencies, ParsedCorpus, CorpusDF
from scattertext.Scalers import percentile_alphabetical
from scattertext.Corpus import Corpus
from scattertext.DocsAndLabelsFromCorpus import DocsAndLabelsFromCorpus, DocsAndLabelsFromCorpusSample


class ScatterChartExplorer(ScatterChart):
    def __init__(self,
                 corpus,
                 **kwargs):
        '''See ScatterChart.  This lets you click on terms to see what contexts they tend to appear in.
        Running the `to_dict` function outputs
        '''
        #if not (isinstance(corpus, (Corpus, ParsedCorpus, CorpusDF, TermCategoryFrequencies))
        #        or (issubclass(type(corpus), (Corpus, ParsedCorpus, CorpusDF, TermCategoryFrequencies)))):
        #    raise AssertionError(corpus, 'of type', type(corpus),
        #                         'must be a subclass of Corpus or TermCategoryFrequencies.')
        ScatterChart.__init__(self, corpus, **kwargs)
        self._term_metadata = None

    def to_dict(self,
                category,
                category_name=None,
                not_category_name=None,
                scores=None,
                metadata=None,
                max_docs_per_category=None,
                transform=percentile_alphabetical,
                alternative_text_field=None,
                title_case_names=False,
                not_categories=None,
                neutral_categories=None,
                extra_categories=None,
                neutral_category_name=None,
                extra_category_name=None,
                background_scorer=None,
                include_term_category_counts=False):
        '''

        Parameters
        ----------
        category : str
            Category to annotate.  Exact value of category.
        category_name : str, optional
            Name of category which will appear on web site. Default None is same as category.
        not_category_name : str, optional
            Name of ~category which will appear on web site. Default None is same as "not " + category.
        scores : np.array, optional
            Scores to use for coloring.  Defaults to None, or RankDifference scores
        metadata, None or array-like.
          List of metadata for each document.  Defaults to a list of blank strings.
        max_docs_per_category, None or int, optional
          Maximum number of documents to store per category.  Defaults to 4.
        transform : function, optional
            Function for ranking terms.  Defaults to scattertext.Scalers.percentile_lexicographic.
        alternative_text_field : str or None, optional
            Field in from dataframe used to make corpus to display in place of parsed text. Only
            can be used if corpus is a ParsedCorpus instance.
        title_case_names : bool, default False
          Should the program title-case the category and not-category names?
        not_categories : list, optional
            List of categories to use as "not category".  Defaults to all others.
        neutral_categories : list, optional
            List of categories to use as neutral.  Defaults [].
        extra_categories : list, optional
            List of categories to use as extra.  Defaults [].
        neutral_category_name : str
            "Neutral" by default. Only active if show_neutral is True.  Name of the neutra l
            column.
        extra_category_name : str
            "Extra" by default. Only active if show_neutral and show_extra are true. Name of the
            extra column.
        background_scorer : CharacteristicScorer, optional
            Used for bg scores
        include_term_category_counts : bool, default False
            Includes term-category counts in keyed off 'term-category-count'. If use_non_text_features,
            use metadata counts instead.

        Returns
        -------
        dictionary {info: {'category_name': full category name, ...},
                    docs: {'texts': [doc1text, ...],
                            'labels': [1, 0, ...],
                            'meta': ['<b>blah</b>', '<b>blah</b>']},

                    // if include_term_category_counts
                    termCounts: [term num -> [total occurrences, total documents, variance], ... for the number of categories]

                    data: {term:term,
                           x:frequency [0-1],
                           y:frequency [0-1],
                           s: score,
                           bg: background score,
                           as: association score,
                           cat25k: freq per 25k in category,
                           cat: count in category,
                           ncat: count in non-category,
                           catdocs: [docnum, ...],
                           ncatdocs: [docnum, ...]
                           ncat25k: freq per 25k in non-category}
                           etc: term specific dictionary (if inject_term_metadata is called and contains terms)}
        '''
        json_data = ScatterChart.to_dict(self,
                                         category,
                                         category_name=category_name,
                                         not_category_name=not_category_name,
                                         scores=scores,
                                         transform=transform,
                                         title_case_names=title_case_names,
                                         not_categories=not_categories,
                                         neutral_categories=neutral_categories,
                                         extra_categories=extra_categories,
                                         background_scorer=background_scorer)
        docs_getter = self._make_docs_getter(max_docs_per_category, alternative_text_field)
        if neutral_category_name is None:
            neutral_category_name = 'Neutral'
        if extra_category_name is None:
            extra_category_name = 'Extra'
        json_data['docs'] = self._get_docs_structure(docs_getter, metadata)
        json_data['info']['neutral_category_name'] = neutral_category_name
        json_data['info']['extra_category_name'] = extra_category_name
        if include_term_category_counts:
            terms = np.array([term_struct['term'] for term_struct in json_data['data']])
            json_data['termCounts'] = self._get_term_doc_counts(terms)
        return json_data

    def _get_term_doc_counts(self, terms):
        term_counts = []
        if self.scatterchartdata.use_non_text_features:
            term_doc_counts = self.term_doc_matrix.get_metadata_doc_count_df('').loc[terms]
            term_doc_freq = self.term_doc_matrix.get_metadata_freq_df('').loc[terms]
        else:
            term_doc_counts = self.term_doc_matrix.get_term_doc_count_df('').loc[terms]
            term_doc_freq = self.term_doc_matrix.get_term_freq_df('').loc[terms]
        # this can possibly be vectorized
        for category_i, category in enumerate(term_doc_freq.columns):
            category_counts = {}
            for term_i, val in enumerate(term_doc_freq[category].values):
                if val > 0:
                    category_counts[term_i] = [val, term_doc_counts.iloc[term_i, category_i]]
            term_counts.append(category_counts)

        return term_counts

    def _make_docs_getter(self, max_docs_per_category, alternative_text_field):
        if max_docs_per_category is None:
            docs_getter = DocsAndLabelsFromCorpus(self.term_doc_matrix,
                                                  alternative_text_field=alternative_text_field)
        else:
            docs_getter = DocsAndLabelsFromCorpusSample(self.term_doc_matrix,
                                                        max_docs_per_category,
                                                        alternative_text_field=alternative_text_field)
        if self.scatterchartdata.use_non_text_features:
            docs_getter = docs_getter.use_non_text_features()
        return docs_getter

    def _get_docs_structure(self, docs_getter, metadata):
        if metadata is not None:
            return docs_getter.get_labels_and_texts_and_meta(np.array(metadata))
        else:
            return docs_getter.get_labels_and_texts()

    def _add_term_freq_to_json_df(self, json_df, term_freq_df, category):
        ScatterChart._add_term_freq_to_json_df(self, json_df, term_freq_df, category)
        json_df['cat'] = term_freq_df[category + ' freq'].astype(np.int)
        json_df['ncat'] = term_freq_df['not cat freq'].astype(np.int)
        if self._term_metadata is not None:
            json_df['etc'] = term_freq_df['term'].apply(lambda term: self._term_metadata.get(term, {}))

    def inject_term_metadata(self, metadata):
        '''

        :param metadata: dict, maps terms to a dictionary which will be added to term's json structure
        :return: ScatterChartExplorer
        '''
        self._term_metadata = metadata
        return self
