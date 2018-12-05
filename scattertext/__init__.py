from __future__ import print_function

import pandas as pd

from scattertext.representations.EmbeddingsResolver import EmbeddingsResolver
from scattertext.termscoring.CohensD import CohensD

version = [0, 0, 2, 31]
__version__ = '.'.join([str(e) for e in version])

import re
import warnings
import numpy as np
import scattertext.viz

from scattertext.diachronic.BubbleDiachronicVisualization import BubbleDiachronicVisualization
from scattertext.diachronic.DiachronicTermMiner import DiachronicTermMiner
from scattertext.characteristic.DenseRankCharacteristicness import DenseRankCharacteristicness
from scattertext.CorpusDF import CorpusDF
from scattertext.CorpusFromFeatureDict import CorpusFromFeatureDict
from scattertext.TermCategoryFrequencies import TermCategoryFrequencies
from scattertext.features.FeatsFromTopicModel import FeatsFromTopicModel
from scattertext.termscoring.BM25Difference import BM25Difference
from scattertext import SampleCorpora
from scattertext import Scalers, ScatterChart
from scattertext import termranking
from scattertext.AsianNLP import chinese_nlp, japanese_nlp
from scattertext.AutoTermSelector import AutoTermSelector
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext.Common import DEFAULT_MINIMUM_TERM_FREQUENCY, DEFAULT_PMI_THRESHOLD_COEFFICIENT
from scattertext.Corpus import Corpus
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.CorpusFromScikit import CorpusFromScikit
from scattertext.Formatter import large_int_format, round_downer
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.PriorFactory import PriorFactory
from scattertext.Scalers import percentile_alphabetical, scale_neg_1_to_1_with_zero_mean_rank_abs_max, \
    scale_neg_1_to_1_with_zero_mean, dense_rank
from scattertext.Scalers import scale_neg_1_to_1_with_zero_mean_abs_max, scale
from scattertext.ScatterChart import ScatterChart
from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory, FeatsFromDoc
from scattertext.TermDocMatrixFilter import TermDocMatrixFilter, filter_bigrams_by_pmis
from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas
from scattertext.TermDocMatrixFromScikit import TermDocMatrixFromScikit
from scattertext.WhitespaceNLP import whitespace_nlp, whitespace_nlp_with_sentences, \
    tweet_tokenzier_factory
from scattertext.external.phrasemachine import phrasemachine
from scattertext.features.FeatsFromGeneralInquirer import FeatsFromGeneralInquirer
from scattertext.features.FeatsFromOnlyEmpath import FeatsFromOnlyEmpath
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc
from scattertext.features.UnigramsFromSpacyDoc import UnigramsFromSpacyDoc
from scattertext.features.FeatsFromSpacyDocAndEmpath import FeatsFromSpacyDocAndEmpath
from scattertext.features.FeatsFromSpacyDocOnlyEmoji import FeatsFromSpacyDocOnlyEmoji
from scattertext.features.FeatsFromSpacyDocOnlyNounChunks import FeatsFromSpacyDocOnlyNounChunks
from scattertext.features.PhraseMachinePhrases \
    import PhraseMachinePhrases, PhraseMachinePhrasesAndUnigrams
from scattertext.indexstore import IndexStoreFromDict
from scattertext.indexstore import IndexStoreFromList
from scattertext.indexstore.IndexStore import IndexStore
from scattertext.representations.Word2VecFromParsedCorpus import Word2VecFromParsedCorpus, \
    Word2VecFromParsedCorpusBigrams
from scattertext.semioticsquare import SemioticSquare, FourSquareAxis
from scattertext.semioticsquare.FourSquare import FourSquare
from scattertext.termranking import OncePerDocFrequencyRanker, DocLengthDividedFrequencyRanker, \
    DocLengthNormalizedFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.termscoring.ScaledFScore import InvalidScalerException, ScaledFScorePresets, \
    ScaledFZScore, ScaledFZScorePrior, ScaledFScorePresetsNeg1To1
from scattertext.termsignificance.LogOddsRatioSmoothed import LogOddsRatioSmoothed
from scattertext.termsignificance.LogOddsRatioInformativeDirichletPiror \
    import LogOddsRatioInformativeDirichletPrior
from scattertext.termsignificance.LogOddsRatioUninformativeDirichletPrior \
    import LogOddsRatioUninformativeDirichletPrior
from scattertext.termsignificance.ScaledFScoreSignificance import ScaledFScoreSignificance
from scattertext.termsignificance.TermSignificance import TermSignificance
from scattertext.viz import VizDataAdapter, HTMLVisualizationAssembly
from scattertext.viz.HTMLSemioticSquareViz import HTMLSemioticSquareViz
from scattertext.semioticsquare.FourSquareAxis import FourSquareAxes
from scattertext.termcompaction.ClassPercentageCompactor import ClassPercentageCompactor
from scattertext.termcompaction.CompactTerms import CompactTerms
from scattertext.termcompaction.PhraseSelector import PhraseSelector
from scattertext.topicmodel.SentencesForTopicModeling import SentencesForTopicModeling
from scattertext.frequencyreaders.DefaultBackgroundFrequencies import DefaultBackgroundFrequencies
from scattertext.termcompaction.DomainCompactor import DomainCompactor
from scattertext.termscoring.ZScores import ZScores
from scattertext.termscoring.RelativeEntropy import RelativeEntropy


def produce_scattertext_html(term_doc_matrix,
                             category,
                             category_name,
                             not_category_name,
                             protocol='https',
                             minimum_term_frequency=DEFAULT_MINIMUM_TERM_FREQUENCY,
                             pmi_threshold_coefficient=DEFAULT_PMI_THRESHOLD_COEFFICIENT,
                             max_terms=None,
                             filter_unigrams=False,
                             height_in_pixels=None,
                             width_in_pixels=None,
                             term_ranker=termranking.AbsoluteFrequencyRanker):
    '''Returns html code of visualization.

    Parameters
    ----------
    term_doc_matrix : TermDocMatrix
        Corpus to use
    category : str
        name of category column
    category_name: str
        name of category to mine for
    not_category_name: str
        name of everything that isn't in category
    protocol : str
        optional, used prototcol of , http or https
    minimum_term_frequency : int, optional
        Minimum number of times word needs to appear to make it into visualization.
    pmi_threshold_coefficient : int, optional
        Filter out bigrams with a PMI of < 2 * pmi_threshold_coefficient. Default is 6.
    max_terms : int, optional
        Maximum number of terms to include in visualization.
    filter_unigrams : bool
        default False, do we filter unigrams that only occur in one bigram
    width_in_pixels: int
        width of viz in pixels, if None, default to JS's choice
    height_in_pixels: int
        height of viz in pixels, if None, default to JS's choice
    term_ranker : TermRanker
            TermRanker class for determining term frequency ranks.

    Returns
    -------
        str, html of visualization
    '''
    scatter_chart_data = ScatterChart(term_doc_matrix=term_doc_matrix,
                                      minimum_term_frequency=minimum_term_frequency,
                                      pmi_threshold_coefficient=pmi_threshold_coefficient,
                                      filter_unigrams=filter_unigrams,
                                      max_terms=max_terms,
                                      term_ranker=term_ranker) \
        .to_dict(category=category,
                 category_name=category_name,
                 not_category_name=not_category_name,
                 transform=percentile_alphabetical)
    html = HTMLVisualizationAssembly(VizDataAdapter(scatter_chart_data),
                                     width_in_pixels,
                                     height_in_pixels).to_html(protocol=protocol)
    return html


def produce_scattertext_explorer(corpus,
                                 category,
                                 category_name=None,
                                 not_category_name=None,
                                 protocol='https',
                                 pmi_threshold_coefficient=DEFAULT_MINIMUM_TERM_FREQUENCY,
                                 minimum_term_frequency=DEFAULT_PMI_THRESHOLD_COEFFICIENT,
                                 minimum_not_category_term_frequency=0,
                                 max_terms=None,
                                 filter_unigrams=False,
                                 height_in_pixels=None,
                                 width_in_pixels=None,
                                 max_snippets=None,
                                 max_docs_per_category=None,
                                 metadata=None,
                                 scores=None,
                                 x_coords=None,
                                 y_coords=None,
                                 original_x=None,
                                 original_y=None,
                                 rescale_x=None,
                                 rescale_y=None,
                                 singleScoreMode=False,
                                 sort_by_dist=False,
                                 reverse_sort_scores_for_not_category=True,
                                 use_full_doc=False,
                                 transform=percentile_alphabetical,
                                 jitter=0,
                                 gray_zero_scores=False,
                                 term_ranker=None,
                                 asian_mode=False,
                                 use_non_text_features=False,
                                 show_top_terms=True,
                                 show_characteristic=True,
                                 word_vec_use_p_vals=False,
                                 max_p_val=0.1,
                                 p_value_colors=False,
                                 term_significance=None,
                                 save_svg_button=False,
                                 x_label=None,
                                 y_label=None,
                                 d3_url=None,
                                 d3_scale_chromatic_url=None,
                                 pmi_filter_thresold=None,
                                 alternative_text_field=None,
                                 terms_to_include=None,
                                 semiotic_square=None,
                                 num_terms_semiotic_square=None,
                                 not_categories=None,
                                 neutral_categories=[],
                                 extra_categories=[],
                                 show_neutral=False,
                                 neutral_category_name=None,
                                 get_tooltip_content=None,
                                 x_axis_values=None,
                                 y_axis_values=None,
                                 color_func=None,
                                 term_scorer=None,
                                 show_axes=True,
                                 horizontal_line_y_position=None,
                                 vertical_line_x_position=None,
                                 show_extra=False,
                                 extra_category_name=None,
                                 censor_points=True,
                                 center_label_over_points=False,
                                 x_axis_labels=None,
                                 y_axis_labels=None,
                                 topic_model_term_lists=None,
                                 topic_model_preview_size=10,
                                 metadata_descriptions=None,
                                 vertical_lines=None,
                                 characteristic_scorer=None,
                                 return_data=False):
    '''Returns html code of visualization.

    Parameters
    ----------
    corpus : Corpus
        Corpus to use.
    category : str
        Name of category column as it appears in original data frame.
    category_name : str
        Name of category to use.  E.g., "5-star reviews."
        Optional, defaults to category name.
    not_category_name : str
        Name of everything that isn't in category.  E.g., "Below 5-star reviews".
        Optional defaults to "N(n)ot " + category_name, with the case of the 'n' dependent
        on the case of the first letter in category_name.
    protocol : str, optional
        Protocol to use.  Either http or https.  Default is https.
    pmi_threshold_coefficient : int, optional
        Filter out bigrams with a PMI of < 2 * pmi_threshold_coefficient. Default is 6
    minimum_term_frequency : int, optional
        Minimum number of times word needs to appear to make it into visualization.
    minimum_not_category_term_frequency : int, optional
      If an n-gram does not occur in the category, minimum times it
       must been seen to be included. Default is 0.
    max_terms : int, optional
        Maximum number of terms to include in visualization.
    filter_unigrams : bool, optional
        Default False, do we filter out unigrams that only occur in one bigram
    width_in_pixels : int, optional
        Width of viz in pixels, if None, default to JS's choice
    height_in_pixels : int, optional
        Height of viz in pixels, if None, default to JS's choice
    max_snippets : int, optional
        Maximum number of snippets to show when term is clicked.  If None, all are shown.
    max_docs_per_category: int, optional
        Maximum number of documents to store per category.  If None, by default, all are stored.
    metadata : list, optional
        list of meta data strings that will be included for each document
    scores : np.array, optional
        Array of term scores or None.
    x_coords : np.array, optional
        Array of term x-axis positions or None.  Must be in [0,1].
        If present, y_coords must also be present.
    y_coords : np.array, optional
        Array of term y-axis positions or None.  Must be in [0,1].
        If present, x_coords must also be present.
    original_x : array-like
        Original, unscaled x-values.  Defaults to x_coords
    original_y : array-like
        Original, unscaled y-values.  Defaults to y_coords
    rescale_x : lambda list[0,1]: list[0,1], optional
        Array of term x-axis positions or None.  Must be in [0,1].
        Rescales x-axis after filtering
    rescale_y : lambda list[0,1]: list[0,1], optional
        Array of term y-axis positions or None.  Must be in [0,1].
        Rescales y-axis after filtering
    singleScoreMode : bool, optional
        Label terms based on score vs distance from corner.  Good for topic scores. Show only one color.
    sort_by_dist: bool, optional
        Label terms based distance from corner. True by default.  Negated by singleScoreMode.
    reverse_sort_scores_for_not_category: bool, optional
        If using a custom score, score the not-category class by
        lowest-score-as-most-predictive. Turn this off for word vector
        or topic similarity. Default True.
    use_full_doc : bool, optional
        Use the full document in snippets.  False by default.
    transform : function, optional
        not recommended for editing.  change the way terms are ranked.  default is st.Scalers.percentile_ordinal
    jitter : float, optional
        percentage of axis to jitter each point.  default is 0.
    gray_zero_scores : bool, optional
        If True, color points with zero-scores a light shade of grey.  False by default.
    term_ranker : TermRanker, optional
        TermRanker class for determining term frequency ranks.
    asian_mode : bool, optional
        Use a special Javascript regular expression that's specific to chinese or japanese
    use_non_text_features : bool, optional
        Show non-bag-of-words features (e.g., Empath) instead of text.  False by default.
    show_top_terms : bool, default True
        Show top terms on the left-hand side of the visualization
    show_characteristic: bool, default True
        Show characteristic terms on the far left-hand side of the visualization
    word_vec_use_p_vals: bool, default False
        Sort by harmonic mean of score and distance.
    max_p_val : float, default 0.1
        If word_vec_use_p_vals, the minimum p val to use.
    p_value_colors : bool, default False
      Color points differently if p val is above 1-max_p_val, below max_p_val, or
       in between.
    term_significance : TermSignificance instance or None
        Way of getting signfiance scores.  If None, p values will not be added.
    save_svg_button : bool, default False
        Add a save as SVG button to the page.
    x_label : str, default None
        Custom x-axis label
    y_label : str, default None
        Custom y-axis label
    d3_url, str, None by default.  The url (or path) of d3.
        URL of d3, to be inserted into <script src="..."/>.  Overrides `protocol`.
      By default, this is `DEFAULT_D3_URL` declared in `HTMLVisualizationAssembly`.
    d3_scale_chromatic_url, str, None by default.  Overrides `protocol`.
      URL of d3 scale chromatic, to be inserted into <script src="..."/>
      By default, this is `DEFAULT_D3_SCALE_CHROMATIC` declared in `HTMLVisualizationAssembly`.
    pmi_filter_thresold : (DEPRECATED) int, None by default
      DEPRECATED.  Use pmi_threshold_coefficient instead.
    alternative_text_field : str or None, optional
        Field in from dataframe used to make corpus to display in place of parsed text. Only
        can be used if corpus is a ParsedCorpus instance.
    terms_to_include : list or None, optional
        Whitelist of terms to include in visualization.
    semiotic_square : SemioticSquare
        None by default.  SemioticSquare based on corpus.  Includes square above visualization.
    num_terms_semiotic_square : int
        10 by default. Number of terms to show in semiotic square.
        Only active if semiotic square is present.
    not_categories : list
        All categories other than category by default.  Documents labeled
        with remaining category.
    neutral_categories : list
        [] by default.  Documents labeled neutral.
    extra_categories : list
        [] by default.  Documents labeled extra.
    show_neutral : bool
        False by default.  Show a third column listing contexts in the
        neutral categories.
    neutral_category_name : str
        "Neutral" by default. Only active if show_neutral is True.  Name of the neutral
        column.
    get_tooltip_content : str
        Javascript function to control content of tooltip.  Function takes a parameter
        which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
        returns a string.
    x_axis_values : list, default None
        Value-labels to show on x-axis. Low, medium, high are defaults.
    y_axis_values : list, default None
        Value-labels to show on y-axis. Low, medium, high are defaults.
    color_func : str, default None
        Javascript function to control color of a point.  Function takes a parameter
        which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
        returns a string.
    term_scorer : Object, default None
        In lieu of scores, object with a get_scores(a,b) function that returns a set of scores,
        where a and b are term counts.  Scorer optionally has a get_term_freqs function.
    show_axes : bool, default True
        Show the ticked axes on the plot.  If false, show inner axes as a crosshair.
    vertical_line_x_position : float, default None
    horizontal_line_y_position : float, default None

    show_extra : bool
        False by default.  Show a fourth column listing contexts in the
        extra categories.
    extra_category_name : str, default None
        "Extra" by default. Only active if show_neutral is True and show_extra is True.  Name
        of the extra column.
    censor_points : bool, default True
        Don't label over points.
    center_label_over_points : bool, default False
        Center a label over points, or try to find a position near a point that
        doesn't overlap anything else.
    x_axis_labels: list, default None
        List of string value-labels to show at evenly spaced intervals on the x-axis.
        Low, medium, high are defaults.
    y_axis_labels : list, default None
        List of string value-labels to show at evenly spaced intervals on the y-axis.
        Low, medium, high are defaults.
    topic_model_term_lists : dict default None
        Dict of metadata name (str) -> List of string terms in metadata. These will be bolded
        in query in context results.
    topic_model_preview_size : int default 10
        Number of terms in topic model to show as a preview.
    metadata_descriptions : dict default None
        Dict of metadata name (str) -> str of metadata description. These will be shown when a meta data term is
        clicked.
    vertical_lines : list default None
        List of floats corresponding to points on the x-axis to draw vertical lines
    characteristic_scorer : CharacteristicScorer default None
        Used for bg scores
    return_data : bool default False
        Return a dict containing the output of `ScatterChartExplorer.to_dict` instead of
        an html.
    Returns
    -------
    str
    html of visualization

    '''
    color = None
    if singleScoreMode or word_vec_use_p_vals:
        color = 'd3.interpolatePurples'
    if singleScoreMode or not sort_by_dist:
        sort_by_dist = False
    else:
        sort_by_dist = True
    if term_ranker is None:
        term_ranker = termranking.AbsoluteFrequencyRanker

    category_name, not_category_name = get_category_names(category, category_name, not_categories, not_category_name)

    if not_categories is None:
        not_categories = [c for c in corpus.get_categories() if c != category]

    if term_scorer:
        # tdf = term_ranker(corpus).get_ranks()
        tdf = corpus.apply_ranker(term_ranker)
        cat_freqs = tdf[category + ' freq']
        if not_categories:
            not_cat_freqs = tdf[[c + ' freq' for c in not_categories]].sum(axis=1)
        else:
            not_cat_freqs = tdf.sum(axis=1) - tdf[category + ' freq']
        scores = term_scorer.get_scores(cat_freqs, not_cat_freqs)

    if pmi_filter_thresold is not None:
        pmi_threshold_coefficient = pmi_filter_thresold
        warnings.warn(
            "The argument name 'pmi_filter_thresold' has been deprecated. Use 'pmi_threshold_coefficient' in its place",
            DeprecationWarning)

    if use_non_text_features:
        pmi_threshold_coefficient = 0

    scatter_chart_explorer = ScatterChartExplorer(corpus,
                                                  minimum_term_frequency=minimum_term_frequency,
                                                  minimum_not_category_term_frequency=minimum_not_category_term_frequency,
                                                  pmi_threshold_coefficient=pmi_threshold_coefficient,
                                                  filter_unigrams=filter_unigrams,
                                                  jitter=jitter,
                                                  max_terms=max_terms,
                                                  term_ranker=term_ranker,
                                                  use_non_text_features=use_non_text_features,
                                                  term_significance=term_significance,
                                                  terms_to_include=terms_to_include, )
    if ((x_coords is None and y_coords is not None)
            or (y_coords is None and x_coords is not None)):
        raise Exception("Both x_coords and y_coords need to be passed or both left blank")
    if x_coords is not None:
        scatter_chart_explorer.inject_coordinates(x_coords,
                                                  y_coords,
                                                  rescale_x=rescale_x,
                                                  rescale_y=rescale_y,
                                                  original_x=original_x,
                                                  original_y=original_y)
    if topic_model_term_lists is not None:
        scatter_chart_explorer.inject_metadata_term_lists(topic_model_term_lists)
    if metadata_descriptions is not None:
        scatter_chart_explorer.inject_metadata_descriptions(metadata_descriptions)
    html_base = None
    if semiotic_square:
        html_base = get_semiotic_square_html(num_terms_semiotic_square,
                                             semiotic_square)
    scatter_chart_data = scatter_chart_explorer.to_dict(category=category,
                                                        category_name=category_name,
                                                        not_category_name=not_category_name,
                                                        not_categories=not_categories,
                                                        transform=transform,
                                                        scores=scores,
                                                        max_docs_per_category=max_docs_per_category,
                                                        metadata=metadata,
                                                        alternative_text_field=alternative_text_field,
                                                        neutral_category_name=neutral_category_name,
                                                        extra_category_name=extra_category_name,
                                                        neutral_categories=neutral_categories,
                                                        extra_categories=extra_categories,
                                                        background_scorer=characteristic_scorer)
    if return_data:
        return scatter_chart_data
    return HTMLVisualizationAssembly(VizDataAdapter(scatter_chart_data),
                                     width_in_pixels=width_in_pixels,
                                     height_in_pixels=height_in_pixels,
                                     max_snippets=max_snippets,
                                     color=color,
                                     grey_zero_scores=gray_zero_scores,
                                     sort_by_dist=sort_by_dist,
                                     reverse_sort_scores_for_not_category=reverse_sort_scores_for_not_category,
                                     use_full_doc=use_full_doc,
                                     asian_mode=asian_mode,
                                     use_non_text_features=use_non_text_features,
                                     show_characteristic=show_characteristic,
                                     show_top_terms=show_top_terms,
                                     word_vec_use_p_vals=word_vec_use_p_vals,
                                     max_p_val=max_p_val,
                                     save_svg_button=save_svg_button,
                                     p_value_colors=p_value_colors,
                                     x_label=x_label,
                                     y_label=y_label,
                                     show_neutral=show_neutral,
                                     get_tooltip_content=get_tooltip_content,
                                     x_axis_values=x_axis_values,
                                     y_axis_values=y_axis_values,
                                     color_func=color_func,
                                     show_axes=show_axes,
                                     show_extra=show_extra,
                                     do_censor_points=censor_points,
                                     center_label_over_points=center_label_over_points,
                                     x_axis_labels=x_axis_labels,
                                     y_axis_labels=y_axis_labels,
                                     topic_model_preview_size=topic_model_preview_size,
                                     vertical_lines=vertical_lines,
                                     horizontal_line_y_position=horizontal_line_y_position,
                                     vertical_line_x_position=vertical_line_x_position) \
        .to_html(protocol=protocol,
                 d3_url=d3_url,
                 d3_scale_chromatic_url=d3_scale_chromatic_url,
                 html_base=html_base)


def get_category_names(category, category_name, not_categories, not_category_name):
    if category_name is None:
        category_name = category
    if not_category_name is None:
        if not_categories is not None and len(not_categories) == 1:
            not_category_name = not_categories[0]
        else:
            not_category_name = ('Not' if category_name[0].isupper() else 'not') + ' ' + category_name
    return category_name, not_category_name


def get_semiotic_square_html(num_terms_semiotic_square, semiotic_square):
    semiotic_square_html = None
    if semiotic_square:
        semiotic_square_viz = HTMLSemioticSquareViz(semiotic_square)
        if num_terms_semiotic_square:
            semiotic_square_html = semiotic_square_viz.get_html(num_terms_semiotic_square)
        else:
            semiotic_square_html = semiotic_square_viz.get_html()
    return semiotic_square_html


def word_similarity_explorer_gensim(corpus,
                                    category,
                                    target_term,
                                    category_name=None,
                                    not_category_name=None,
                                    word2vec=None,
                                    alpha=0.01,
                                    max_p_val=0.1,
                                    term_significance=None,
                                    **kwargs):
    '''
        Parameters
        ----------
        corpus : Corpus
            Corpus to use.
        category : str
            Name of category column as it appears in original data frame.
        category_name : str
            Name of category to use.  E.g., "5-star reviews."
        not_category_name : str
            Name of everything that isn't in category.  E.g., "Below 5-star reviews".
        target_term : str
            Word or phrase for semantic similarity comparison
        word2vec : word2vec.Word2Vec
          Gensim-compatible Word2Vec model of lower-cased corpus. If none, o
          ne will be trained using Word2VecFromParsedCorpus(corpus).train()
        alpha : float, default = 0.01
            Uniform dirichlet prior for p-value calculation
        max_p_val : float, default = 0.1
            Max p-val to use find set of terms for similarity calculation
        term_significance : TermSignificance
            Significance finder

        Remaining arguments are from `produce_scattertext_explorer`.
        Returns
        -------
            str, html of visualization
        '''

    if word2vec is None:
        word2vec = Word2VecFromParsedCorpus(corpus).train()

    if term_significance is None:
        term_significance = LogOddsRatioUninformativeDirichletPrior(alpha)
    assert issubclass(type(term_significance), TermSignificance)

    scores = []

    for tok in corpus._term_idx_store._i2val:
        try:
            scores.append(word2vec.similarity(target_term, tok.replace(' ', '_')))
        except:
            try:
                scores.append(np.mean([word2vec.similarity(target_term, tok_part)
                                       for tok_part in tok.split()]))
            except:
                scores.append(0)
    scores = np.array(scores)

    return produce_scattertext_explorer(corpus,
                                        category,
                                        category_name,
                                        not_category_name,
                                        scores=scores,
                                        sort_by_dist=False,
                                        reverse_sort_scores_for_not_category=False,
                                        word_vec_use_p_vals=True,
                                        term_significance=term_significance,
                                        max_p_val=max_p_val,
                                        p_value_colors=True,
                                        **kwargs)


def word_similarity_explorer(corpus,
                             category,
                             category_name,
                             not_category_name,
                             target_term,
                             nlp=None,
                             alpha=0.01,
                             max_p_val=0.1,
                             **kwargs):
    '''
    Parameters
    ----------
    corpus : Corpus
        Corpus to use.
    category : str
        Name of category column as it appears in original data frame.
    category_name : str
        Name of category to use.  E.g., "5-star reviews."
    not_category_name : str
        Name of everything that isn't in category.  E.g., "Below 5-star reviews".
    target_term : str
        Word or phrase for semantic similarity comparison
    nlp : spaCy-like parsing function
        E.g., spacy.load('en'), whitespace_nlp, etc...
    alpha : float, default = 0.01
        Uniform dirichlet prior for p-value calculation
    max_p_val : float, default = 0.1
        Max p-val to use find set of terms for similarity calculation
    Remaining arguments are from `produce_scattertext_explorer`.
    Returns
    -------
        str, html of visualization
    '''

    if nlp is None:
        import spacy
        nlp = spacy.load('en')

    base_term = nlp(target_term)
    scores = np.array([base_term.similarity(nlp(tok))
                       for tok
                       in corpus._term_idx_store._i2val])
    return produce_scattertext_explorer(corpus,
                                        category,
                                        category_name,
                                        not_category_name,
                                        scores=scores,
                                        sort_by_dist=False,
                                        reverse_sort_scores_for_not_category=False,
                                        word_vec_use_p_vals=True,
                                        term_significance=LogOddsRatioUninformativeDirichletPrior(alpha),
                                        max_p_val=max_p_val,
                                        p_value_colors=True,
                                        **kwargs)


def produce_frequency_explorer(corpus,
                               category,
                               category_name=None,
                               not_category_name=None,
                               term_ranker=termranking.AbsoluteFrequencyRanker,
                               alpha=0.01,
                               use_term_significance=False,
                               term_scorer=None,
                               not_categories=None,
                               grey_threshold=1.96,
                               y_axis_values=None,
                               **kwargs):
    '''
    Produces a Monroe et al. style visualization, with the x-axis being the log frequency

    Parameters
    ----------
    corpus : Corpus
        Corpus to use.
    category : str
        Name of category column as it appears in original data frame.
    category_name : str or None
        Name of category to use.  E.g., "5-star reviews."
        Defaults to category
    not_category_name : str or None
        Name of everything that isn't in category.  E.g., "Below 5-star reviews".
        Defaults to "Not " + category_name
    term_ranker : TermRanker
        TermRanker class for determining term frequency ranks.
    alpha : float, default = 0.01
        Uniform dirichlet prior for p-value calculation
    use_term_significance : bool, True by default
        Use term scorer
    term_scorer : TermSignificance
        Subclass of TermSignificance to use as for scores and significance
    not_categories : list
        All categories other than category by default.  Documents labeled
        with remaining category.
    grey_threshold : float
        Score to grey points. Default is 1.96
    y_axis_values : list
        Custom y-axis values. Defaults to linspace
    Remaining arguments are from `produce_scattertext_explorer`.'
    Returns
    -------
        str, html of visualization
    '''

    if not_categories is None:
        not_categories = [c for c in corpus.get_categories() if c != category]
    if term_scorer is None:
        term_scorer = LogOddsRatioUninformativeDirichletPrior(alpha)

    my_term_ranker = term_ranker(corpus)
    if kwargs.get('use_non_text_features', False):
        my_term_ranker.use_non_text_features()
    term_freq_df = my_term_ranker.get_ranks() + 1
    freqs = term_freq_df[[c + ' freq' for c in [category] + not_categories]].sum(axis=1).values
    x_axis_values = [round_downer(10 ** x) for x
                     in np.linspace(0, np.log(freqs.max()) / np.log(10), 5)]
    x_axis_values = [x for x in x_axis_values if x > 1 and x <= freqs.max()]
    # y_axis_values = [-2.58, -1.96, 0, 1.96, 2.58]
    frequencies_log_scaled = scale(np.log(freqs) - np.log(1))

    if 'scores' not in kwargs:
        zeta_i_j = term_scorer.get_scores(
            term_freq_df[category + ' freq'],
            term_freq_df[[c + ' freq' for c in not_categories]].sum(axis=1)
        )
        kwargs['scores'] = kwargs.get('scores', zeta_i_j)

    def y_axis_rescale(coords):
        return ((coords - 0.5) / (np.abs(coords - 0.5).max()) + 1) / 2

    # from https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
    def round_to_1(x):
        if x == 0:
            return 0
        return round(x, -int(np.floor(np.log10(abs(x)))))

    if y_axis_values is None:
        '''
        y_axis_values = [round_to_1(x) for x
                         in sorted(set(-np.linspace(0, np.max(np.abs(kwargs['scores'])), 4))
                                   | set(np.linspace(0, np.max(np.abs(kwargs['scores'])), 4))
                                   | {0})]
        '''
        max_score = np.floor(np.max(kwargs['scores']) * 100) / 100
        min_score = np.ceil(np.min(kwargs['scores']) * 100) / 100
        if min_score < 0 and max_score > 0:
            central = 0
        else:
            central = 0.5
        y_axis_values = [x for x in [min_score, central, max_score]
                         if x >= min_score and x <= max_score]
    scores_scaled_for_charting = scale_neg_1_to_1_with_zero_mean_abs_max(kwargs['scores'])
    # kwargs['metadata'] = kwargs.get('metadata', None),
    if use_term_significance:
        kwargs['term_significance'] = term_scorer

    color_func = '''(function(d) {
	return (Math.abs(d.os) < %s) 
	 ? d3.interpolate(d3.rgb(230, 230, 230), d3.rgb(130, 130, 130))(Math.abs(d.os)/%s) 
	 : d3.interpolateRdYlBu(d.y);
	})''' % (grey_threshold, grey_threshold)

    return produce_scattertext_explorer(corpus,
                                        category=category,
                                        category_name=category_name,
                                        not_category_name=not_category_name,
                                        x_coords=frequencies_log_scaled,
                                        y_coords=scores_scaled_for_charting,
                                        original_x=freqs,
                                        original_y=kwargs['scores'],
                                        x_axis_values=x_axis_values,
                                        y_axis_values=y_axis_values,
                                        rescale_x=scale,
                                        rescale_y=y_axis_rescale,
                                        sort_by_dist=False,
                                        term_ranker=term_ranker,
                                        color_func=color_func,
                                        not_categories=not_categories,
                                        x_label=kwargs.get('x_label', 'Log Frequency'),
                                        y_label=kwargs.get('y_label', term_scorer.get_name()),
                                        **kwargs)


# for legacy reasons
produce_fightin_words_explorer = produce_frequency_explorer


def produce_semiotic_square_explorer(semiotic_square,
                                     x_label,
                                     y_label,
                                     category_name=None,
                                     not_category_name=None,
                                     neutral_category_name=None,
                                     num_terms_semiotic_square=None,
                                     get_tooltip_content=None,
                                     x_axis_values=None,
                                     y_axis_values=None,
                                     color_func=None,
                                     axis_scaler=scale_neg_1_to_1_with_zero_mean,
                                     **kwargs):
    '''
    Produces a semiotic square visualization.

    Parameters
    ----------
    semiotic_square : SemioticSquare
        The basis of the visualization
    x_label : str
        The x-axis label in the scatter plot.  Relationship between `category_a` and `category_b`.
    y_label
        The y-axis label in the scatter plot.  Relationship neutral term and complex term.
    category_name : str or None
        Name of category to use.  Defaults to category_a.
    not_category_name : str or None
        Name of everything that isn't in category.  Defaults to category_b.
    neutral_category_name : str or None
        Name of neutral set of data.  Defaults to "Neutral".
    num_terms_semiotic_square : int or None
        10 by default. Number of terms to show in semiotic square.
    get_tooltip_content : str or None
        Defaults to tooltip showing z-scores on both axes.
    x_axis_values : list, default None
        Value-labels to show on x-axis. [-2.58, -1.96, 0, 1.96, 2.58] is the default
    y_axis_values : list, default None
        Value-labels to show on y-axis. [-2.58, -1.96, 0, 1.96, 2.58] is the default
    color_func : str, default None
        Javascript function to control color of a point.  Function takes a parameter
        which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
        returns a string. Defaults to RdYlBl on x-axis, and varying saturation on y-axis.
    axis_scaler : lambda, default scale_neg_1_to_1_with_zero_mean_abs_max
        Scale values to fit axis
    Remaining arguments are from `produce_scattertext_explorer`.

    Returns
    -------
        str, html of visualization
    '''
    if category_name is None:
        category_name = semiotic_square.category_a_
    if not_category_name is None:
        not_category_name = semiotic_square.category_b_

    if get_tooltip_content is None:
        get_tooltip_content = '''(function(d) {return d.term + "<br/>%s: " + Math.round(d.ox*1000)/1000+"<br/>%s: " + Math.round(d.oy*1000)/1000})''' \
                              % (x_label, y_label)
    if color_func is None:
        # this desaturates
        # color_func = '(function(d) {var c = d3.hsl(d3.interpolateRdYlBu(d.x)); c.s *= d.y; return c;})'
        color_func = '(function(d) {return d3.interpolateRdYlBu(d.x)})'
    '''
    my_scaler = scale_neg_1_to_1_with_zero_mean_abs_max
    if foveate:
        my_scaler = scale_neg_1_to_1_with_zero_mean_rank_abs_max
    '''
    axes = semiotic_square.get_axes()
    return produce_scattertext_explorer(semiotic_square.term_doc_matrix_,
                                        category=semiotic_square.category_a_,
                                        category_name=category_name,
                                        not_category_name=not_category_name,
                                        not_categories=[semiotic_square.category_b_],
                                        scores=-axes['x'],
                                        sort_by_dist=False,
                                        x_coords=axis_scaler(-axes['x']),
                                        y_coords=axis_scaler(axes['y']),
                                        original_x=-axes['x'],
                                        original_y=axes['y'],
                                        show_characteristic=False,
                                        show_top_terms=False,
                                        x_label=x_label,
                                        y_label=y_label,
                                        semiotic_square=semiotic_square,
                                        neutral_categories=semiotic_square.neutral_categories_,
                                        show_neutral=True,
                                        neutral_category_name=neutral_category_name,
                                        num_terms_semiotic_square=num_terms_semiotic_square,
                                        get_tooltip_content=get_tooltip_content,
                                        x_axis_values=x_axis_values,
                                        y_axis_values=y_axis_values,
                                        color_func=color_func,
                                        show_axes=False,
                                        **kwargs)


def produce_four_square_explorer(four_square,
                                 x_label=None,
                                 y_label=None,
                                 a_category_name=None,
                                 b_category_name=None,
                                 not_a_category_name=None,
                                 not_b_category_name=None,
                                 num_terms_semiotic_square=None,
                                 get_tooltip_content=None,
                                 x_axis_values=None,
                                 y_axis_values=None,
                                 color_func=None,
                                 axis_scaler=scale_neg_1_to_1_with_zero_mean,
                                 **kwargs):
    '''
    Produces a semiotic square visualization.

    Parameters
    ----------
    four_square : FourSquare
        The basis of the visualization
    x_label : str
        The x-axis label in the scatter plot.  Relationship between `category_a` and `category_b`.
    y_label
        The y-axis label in the scatter plot.  Relationship neutral term and complex term.
    a_category_name : str or None
        Name of category to use.  Defaults to category_a.
    b_category_name : str or None
        Name of everything that isn't in category.  Defaults to category_b.
    not_a_category_name : str or None
        Name of neutral set of data.  Defaults to "Neutral".
    not_b_category_name: str or None
        Name of neutral set of data.  Defaults to "Extra".
    num_terms_semiotic_square : int or None
        10 by default. Number of terms to show in semiotic square.
    get_tooltip_content : str or None
        Defaults to tooltip showing z-scores on both axes.
    x_axis_values : list, default None
        Value-labels to show on x-axis. [-2.58, -1.96, 0, 1.96, 2.58] is the default
    y_axis_values : list, default None
        Value-labels to show on y-axis. [-2.58, -1.96, 0, 1.96, 2.58] is the default
    color_func : str, default None
        Javascript function to control color of a point.  Function takes a parameter
        which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
        returns a string. Defaults to RdYlBl on x-axis, and varying saturation on y-axis.
    axis_scaler : lambda, default scale_neg_1_to_1_with_zero_mean_abs_max
        Scale values to fit axis
    Remaining arguments are from `produce_scattertext_explorer`.

    Returns
    -------
        str, html of visualization
    '''
    if a_category_name is None:
        a_category_name = four_square.get_labels()['a_label']
        if a_category_name is None or a_category_name == '':
            a_category_name = four_square.category_a_list_[0]
    if b_category_name is None:
        b_category_name = four_square.get_labels()['b_label']
        if b_category_name is None or b_category_name == '':
            b_category_name = four_square.category_b_list_[0]
    if not_a_category_name is None:
        not_a_category_name = four_square.get_labels()['not_a_label']
        if not_a_category_name is None or not_a_category_name == '':
            not_a_category_name = four_square.not_category_a_list_[0]
    if not_b_category_name is None:
        not_b_category_name = four_square.get_labels()['not_b_label']
        if not_b_category_name is None or not_b_category_name == '':
            not_b_category_name = four_square.not_category_b_list_[0]

    if x_label is None:
        x_label = a_category_name + '-' + b_category_name
    if y_label is None:
        y_label = not_a_category_name + '-' + not_b_category_name

    if get_tooltip_content is None:
        get_tooltip_content = '''(function(d) {return d.term + "<br/>%s: " + Math.round(d.ox*1000)/1000+"<br/>%s: " + Math.round(d.oy*1000)/1000})''' \
                              % (x_label, y_label)
    if color_func is None:
        # this desaturates
        # color_func = '(function(d) {var c = d3.hsl(d3.interpolateRdYlBu(d.x)); c.s *= d.y; return c;})'
        color_func = '(function(d) {return d3.interpolateRdYlBu(d.x)})'
    '''
    my_scaler = scale_neg_1_to_1_with_zero_mean_abs_max
    if foveate:
        my_scaler = scale_neg_1_to_1_with_zero_mean_rank_abs_max
    '''
    axes = four_square.get_axes()
    if 'scores' not in kwargs:
        kwargs['scores'] = -axes['x']

    return produce_scattertext_explorer(
        four_square.term_doc_matrix_,
        category=list(set(four_square.category_a_list_) - set(four_square.category_b_list_))[0],
        category_name=a_category_name,
        not_category_name=b_category_name,
        not_categories=four_square.category_b_list_,
        neutral_categories=four_square.not_category_a_list_,
        extra_categories=four_square.not_category_b_list_,
        sort_by_dist=False,
        x_coords=axis_scaler(-axes['x']),
        y_coords=axis_scaler(axes['y']),
        original_x=-axes['x'],
        original_y=axes['y'],
        show_characteristic=False,
        show_top_terms=False,
        x_label=x_label,
        y_label=y_label,
        semiotic_square=four_square,
        show_neutral=True,
        neutral_category_name=not_a_category_name,
        show_extra=True,
        extra_category_name=not_b_category_name,
        num_terms_semiotic_square=num_terms_semiotic_square,
        get_tooltip_content=get_tooltip_content,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        color_func=color_func,
        show_axes=False,
        **kwargs)


def produce_four_square_axes_explorer(four_square_axes,
                                      x_label=None,
                                      y_label=None,
                                      num_terms_semiotic_square=None,
                                      get_tooltip_content=None,
                                      x_axis_values=None,
                                      y_axis_values=None,
                                      color_func=None,
                                      axis_scaler=scale_neg_1_to_1_with_zero_mean,
                                      **kwargs):
    '''
    Produces a semiotic square visualization.

    Parameters
    ----------
    four_square : FourSquareAxes
        The basis of the visualization
    x_label : str
        The x-axis label in the scatter plot.  Relationship between `category_a` and `category_b`.
    y_label
        The y-axis label in the scatter plot.  Relationship neutral term and complex term.
    not_b_category_name: str or None
        Name of neutral set of data.  Defaults to "Extra".
    num_terms_semiotic_square : int or None
        10 by default. Number of terms to show in semiotic square.
    get_tooltip_content : str or None
        Defaults to tooltip showing z-scores on both axes.
    x_axis_values : list, default None
        Value-labels to show on x-axis. [-2.58, -1.96, 0, 1.96, 2.58] is the default
    y_axis_values : list, default None
        Value-labels to show on y-axis. [-2.58, -1.96, 0, 1.96, 2.58] is the default
    color_func : str, default None
        Javascript function to control color of a point.  Function takes a parameter
        which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
        returns a string. Defaults to RdYlBl on x-axis, and varying saturation on y-axis.
    axis_scaler : lambda, default scale_neg_1_to_1_with_zero_mean_abs_max
        Scale values to fit axis
    Remaining arguments are from `produce_scattertext_explorer`.

    Returns
    -------
        str, html of visualization
    '''

    if x_label is None:
        x_label = four_square_axes.left_category_name_ + '-' + four_square_axes.right_category_name_
    if y_label is None:
        y_label = four_square_axes.top_category_name_ + '-' + four_square_axes.bottom_category_name_

    if get_tooltip_content is None:
        get_tooltip_content = '''(function(d) {return d.term + "<br/>%s: " + Math.round(d.ox*1000)/1000+"<br/>%s: " + Math.round(d.oy*1000)/1000})''' \
                              % (x_label, y_label)
    if color_func is None:
        # this desaturates
        # color_func = '(function(d) {var c = d3.hsl(d3.interpolateRdYlBu(d.x)); c.s *= d.y; return c;})'
        color_func = '(function(d) {return d3.interpolateRdYlBu(d.x)})'
    axes = four_square_axes.get_axes()

    if 'scores' not in kwargs:
        kwargs['scores'] = -axes['x']

    '''
    my_scaler = scale_neg_1_to_1_with_zero_mean_abs_max
    if foveate:
        my_scaler = scale_neg_1_to_1_with_zero_mean_rank_abs_max
    '''
    return produce_scattertext_explorer(
        four_square_axes.term_doc_matrix_,
        category=four_square_axes.left_categories_[0],
        category_name=four_square_axes.left_category_name_,
        not_categories=four_square_axes.right_categories_,
        not_category_name=four_square_axes.right_category_name_,
        neutral_categories=four_square_axes.top_categories_,
        neutral_category_name=four_square_axes.top_category_name_,
        extra_categories=four_square_axes.bottom_categories_,
        extra_category_name=four_square_axes.bottom_category_name_,
        sort_by_dist=False,
        x_coords=axis_scaler(-axes['x']),
        y_coords=axis_scaler(axes['y']),
        original_x=-axes['x'],
        original_y=axes['y'],
        show_characteristic=False,
        show_top_terms=False,
        x_label=x_label,
        y_label=y_label,
        semiotic_square=four_square_axes,
        show_neutral=True,
        show_extra=True,
        num_terms_semiotic_square=num_terms_semiotic_square,
        get_tooltip_content=get_tooltip_content,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        color_func=color_func,
        show_axes=False,
        **kwargs
    )


def produce_projection_explorer(corpus,
                                category,
                                word2vec_model=None,
                                projection_model=None,
                                embeddings=None,
                                term_acceptance_re=re.compile('[a-z]{3,}'),
                                show_axes=False,
                                **kwargs):
    '''
    Parameters
    ----------
    corpus : ParsedCorpus
        It is highly recommended to use a stoplisted, unigram corpus-- `corpus.get_stoplisted_unigram_corpus()`
    category : str
    word2vec_model : Word2Vec
        A gensim word2vec model.  A default model will be used instead. See Word2VecFromParsedCorpus for the default
        model.
    projection_model : sklearn-style dimensionality reduction model.
        By default: umap.UMAP(min_dist=0.5, metric='cosine')
      You could also use, e.g., sklearn.manifold.TSNE(perplexity=10, n_components=2, init='pca', n_iter=2500, random_state=23)
    embeddings : array[len(corpus.get_terms()), X]
        Word embeddings.  If None (default), wil train them using word2vec Model
    term_acceptance_re : SRE_Pattern,
        Regular expression to identify valid terms
    show_axes : bool, default False
        Show the ticked axes on the plot.  If false, show inner axes as a crosshair.
    kwargs : dict
        Remaining produce_scattertext_explorer keywords get_tooltip_content

    Returns
    -------
    str
    HTML of visualization

    '''
    embeddings_resolover = EmbeddingsResolver(corpus)
    if embeddings is not None:
        embeddings_resolover.set_embeddings(embeddings)
    else:
        embeddings_resolover.set_embeddings_model(word2vec_model, term_acceptance_re)
    corpus, word_axes = embeddings_resolover.project_embeddings(projection_model, x_dim=0, y_dim=1)
    html = produce_scattertext_explorer(
        corpus=corpus,
        category=category,
        minimum_term_frequency=0,
        sort_by_dist=False,
        x_coords=scale(word_axes['x']),
        y_coords=scale(word_axes['y']),
        y_label='',
        x_label='',
        show_axes=show_axes,
        **kwargs
    )
    return html


def produce_pca_explorer(corpus,
                         category,
                         word2vec_model=None,
                         projection_model=None,
                         embeddings=None,
                         projection=None,
                         term_acceptance_re=re.compile('[a-z]{3,}'),
                         x_dim=0,
                         y_dim=1,
                         scaler=scale,
                         show_axes=False,
                         show_dimensions_on_tooltip=True,
                         **kwargs):
    """
    Parameters
    ----------
    corpus : ParsedCorpus
        It is highly recommended to use a stoplisted, unigram corpus-- `corpus.get_stoplisted_unigram_corpus()`
    category : str
    word2vec_model : Word2Vec
        A gensim word2vec model.  A default model will be used instead. See Word2VecFromParsedCorpus for the default
        model.
    projection_model : sklearn-style dimensionality reduction model. Ignored if 'projection' is presents
        By default: umap.UMAP(min_dist=0.5, metric='cosine') unless projection is present. If so,
        You could also use, e.g., sklearn.manifold.TSNE(perplexity=10, n_components=2, init='pca', n_iter=2500, random_state=23)
    embeddings : array[len(corpus.get_terms()), X]
        Word embeddings.  If None (default), and no value is passed into projection, use word2vec_model
    projection : DataFrame('x': array[len(corpus.get_terms())], 'y': array[len(corpus.get_terms())])
        If None (default), produced using projection_model
    term_acceptance_re : SRE_Pattern,
        Regular expression to identify valid terms
    x_dim : int, default 0
        Dimension of transformation matrix for x-axis
    y_dim : int, default 1
        Dimension of transformation matrix for y-axis
    scalers : function , default scattertext.Scalers.scale
        Function used to scale projection
    show_axes : bool, default False
        Show the ticked axes on the plot.  If false, show inner axes as a crosshair.
    show_dimensions_on_tooltip : bool, False by default
        If true, shows dimension positions on tooltip, along with term name. Otherwise, default to the
         get_tooltip_content parameter.
    kwargs : dict
        Remaining produce_scattertext_explorer keywords get_tooltip_content

    Returns
    -------
    str
    HTML of visualization
    """
    if projection is None:
        embeddings_resolover = EmbeddingsResolver(corpus)
        if embeddings is not None:
            embeddings_resolover.set_embeddings(embeddings)
        else:
            embeddings_resolover.set_embeddings_model(word2vec_model, term_acceptance_re)
        corpus, projection = embeddings_resolover.project_embeddings(projection_model, x_dim=x_dim, y_dim=y_dim)
    else:
        assert type(projection) == pd.DataFrame
        assert 'x' in projection and 'y' in projection
        assert set(projection.index) == set(corpus.get_terms())
    if show_dimensions_on_tooltip:
        kwargs['get_tooltip_content'] = '''(function(d) {
     return  d.term + "<br/>Dim %s: " + Math.round(d.ox*1000)/1000 + "<br/>Dim %s: " + Math.round(d.oy*1000)/1000 
    })''' % (x_dim, y_dim)
    html = produce_scattertext_explorer(
        corpus=corpus,
        category=category,
        minimum_term_frequency=0,
        sort_by_dist=False,
        original_x=projection['x'],
        original_y=projection['y'],
        x_coords=scaler(projection['x']),
        y_coords=scaler(projection['y']),
        y_label='',
        x_label='',
        show_axes=show_axes,
        horizontal_line_y_position=0,
        vertical_line_x_position=0,
        **kwargs
    )
    return html

def produce_characteristic_explorer(corpus,
                                    category,
                                    category_name=None,
                                    not_category_name=None,
                                    not_categories=None,
                                    characteristic_scorer=DenseRankCharacteristicness(),
                                    term_ranker=termranking.AbsoluteFrequencyRanker,
                                    term_scorer=RankDifference(),
                                    **kwargs):
    '''
    Parameters
    ----------
    corpus : Corpus
        It is highly recommended to use a stoplisted, unigram corpus-- `corpus.get_stoplisted_unigram_corpus()`
    category : str
    category_name : str
    not_category_name : str
    not_categories : list
    characteristic_scorer : CharacteristicScorer
    term_ranker
    term_scorer
    term_acceptance_re : SRE_Pattern
        Regular expression to identify valid terms
    kwargs : dict
        remaining produce_scattertext_explorer keywords

    Returns
    -------
    str HTML of visualization

    '''
    if not_categories is None:
        not_categories = [c for c in corpus.get_categories() if c != category]

    category_name, not_category_name = get_category_names(
        category, category_name, not_categories, not_category_name)

    zero_point, characteristic_scores = characteristic_scorer.get_scores(corpus)
    corpus = corpus.remove_terms(set(corpus.get_terms()) - set(characteristic_scores.index))
    characteristic_scores = characteristic_scores.loc[corpus.get_terms()]
    term_freq_df = term_ranker(corpus).get_ranks()
    scores = term_scorer.get_scores(
        term_freq_df[category + ' freq'],
        term_freq_df[[c + ' freq' for c in not_categories]].sum(axis=1)
    )
    kwargs['scores'] = kwargs.get('scores', scores)
    max_score = np.floor(np.max(kwargs['scores']) * 100) / 100
    min_score = np.ceil(np.min(kwargs['scores']) * 100) / 100
    if min_score < 0 and max_score > 0:
        central = 0
    else:
        central = 0.5
    scores_scaled_for_charting = scale_neg_1_to_1_with_zero_mean_abs_max(kwargs['scores'])
    html = produce_scattertext_explorer(
        corpus=corpus,
        category=category,
        category_name=category_name,
        not_category_name=not_category_name,
        not_categories=not_categories,
        minimum_term_frequency=0,
        sort_by_dist=False,
        x_coords=characteristic_scores,
        y_coords=scores_scaled_for_charting,
        y_axis_labels=kwargs.get('y_axis_labels',
                                 ['More ' + not_category_name,
                                  'Even',
                                  'More ' + category_name]),
        x_label=kwargs.get('x_label', 'Characteristic to Corpus'),
        y_label=kwargs.get('y_label', term_scorer.get_name()),
        vertical_lines=kwargs.get('vertical_lines', []),
        characteristic_scorer=kwargs.get('characteristic_scorer', characteristic_scorer),
        **kwargs
    )
    return html


def sparse_explorer(corpus,
                    category,
                    scores,
                    category_name=None,
                    not_category_name=None,
                    **kwargs):
    '''
    Parameters
    ----------
    corpus : Corpus
        Corpus to use.
    category : str
        Name of category column as it appears in original data frame.
    category_name : str
        Name of category to use.  E.g., "5-star reviews."
    not_category_name : str
        Name of everything that isn't in category.  E.g., "Below 5-star reviews".
    scores : np.array
        Scores to display in visualization.  Zero scores are grey.

    Remaining arguments are from `produce_scattertext_explorer`.

    Returns
    -------
        str, html of visualization
    '''

    return produce_scattertext_explorer(
        corpus,
        category,
        category_name,
        not_category_name,
        scores=scores,
        sort_by_dist=False,
        gray_zero_scores=True,
        **kwargs
    )
