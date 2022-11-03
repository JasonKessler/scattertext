from __future__ import print_function


version = [0, 1, 8]
__version__ = '.'.join([str(e) for e in version])

import re
import numpy as np
import pandas as pd
import warnings
from scattertext.features.UseFullDocAsFeature import UseFullDocAsFeature
from scattertext.features.UseFullDocAsMetadata import UseFullDocAsMetadata
from scattertext.graphs.ComponentDiGraph import ComponentDiGraph
from scattertext.graphs.ComponentDiGraphHTMLRenderer import ComponentDiGraphHTMLRenderer
from scattertext.graphs.GraphStructure import GraphStructure
from scattertext.graphs.SimpleDiGraph import SimpleDiGraph
from scattertext.features.FeatsFromSentencePiece import FeatsFromSentencePiece
from scattertext.features.PyTextRankPhrases import PyTextRankPhrases
from scattertext.termscoring.BetaPosterior import BetaPosterior
from scattertext.semioticsquare.SemioticSquareFromAxes import SemioticSquareFromAxes
from scattertext.categoryprojector.OptimalProjection import get_optimal_category_projection, \
    get_optimal_category_projection_by_rank, ProjectionQuality
from scattertext.categoryprojector.CategoryProjector import CategoryProjector, Doc2VecCategoryProjector, \
    LengthNormalizer
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer
from scattertext.viz.BasicHTMLFromScatterplotStructure import BasicHTMLFromScatterplotStructure, D3URLs
import scattertext.viz
from scattertext.CategoryColorAssigner import CategoryColorAssigner
from scattertext.representations.EmbeddingsResolver import EmbeddingsResolver
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor, TermCategoryRanker, \
    AssociationCompactorByRank, JSDCompactor
from scattertext.termscoring.CohensD import CohensD, HedgesR
from scattertext.termscoring.MannWhitneyU import MannWhitneyU
from scattertext.diachronic.BubbleDiachronicVisualization import BubbleDiachronicVisualization
from scattertext.diachronic.DiachronicTermMiner import DiachronicTermMiner
from scattertext.characteristic.DenseRankCharacteristicness import DenseRankCharacteristicness
from scattertext.CorpusDF import CorpusDF
from scattertext.CorpusFromFeatureDict import CorpusFromFeatureDict
from scattertext.TermCategoryFrequencies import TermCategoryFrequencies
from scattertext.features.FeatsFromTopicModel import FeatsFromTopicModel
from scattertext.termscoring.BM25Difference import BM25Difference
from scattertext import SampleCorpora, SampleLexicons, smoothing
from scattertext import Scalers, ScatterChart
from scattertext import termranking
from scattertext.AsianNLP import chinese_nlp, japanese_nlp
from scattertext.AutoTermSelector import AutoTermSelector
from scattertext.CSRMatrixTools import CSRMatrixFactory
from scattertext import Common
from scattertext.Common import DEFAULT_MINIMUM_TERM_FREQUENCY, DEFAULT_PMI_THRESHOLD_COEFFICIENT, MY_ENGLISH_STOP_WORDS
from scattertext.Corpus import Corpus
from scattertext.CorpusFromPandas import CorpusFromPandas
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments
from scattertext.CorpusFromScikit import CorpusFromScikit
from scattertext.Formatter import large_int_format, round_downer
from scattertext.PriorFactory import PriorFactory
from scattertext.Scalers import percentile_alphabetical, scale_neg_1_to_1_with_zero_mean_rank_abs_max, \
    scale_neg_1_to_1_with_zero_mean, dense_rank, stretch_0_to_1
from scattertext.Scalers import scale_neg_1_to_1_with_zero_mean_abs_max, scale
from scattertext.ScatterChart import ScatterChart
from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.TermDocMatrixFactory import TermDocMatrixFactory, FeatsFromDoc
from scattertext.TermDocMatrixFilter import TermDocMatrixFilter, filter_bigrams_by_pmis
from scattertext.TermDocMatrixFromPandas import TermDocMatrixFromPandas
from scattertext.TermDocMatrixFromScikit import TermDocMatrixFromScikit
from scattertext.WhitespaceNLP import whitespace_nlp, whitespace_nlp_with_sentences, \
    tweet_tokenizier_factory
from scattertext.external.phrasemachine import phrasemachine
from scattertext.features.FeatsFromGeneralInquirer import FeatsFromGeneralInquirer
from scattertext.features.FeatsFromMoralFoundationsDictionary import FeatsFromMoralFoundationsDictionary
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
    Word2VecFromParsedCorpusBigrams, CorpusAdapterForGensim
from scattertext.semioticsquare import SemioticSquare, FourSquareAxis
from scattertext.semioticsquare.FourSquare import FourSquare
from scattertext.termranking import OncePerDocFrequencyRanker, DocLengthDividedFrequencyRanker, \
    DocLengthNormalizedFrequencyRanker, AbsoluteFrequencyRanker
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.termscoring.ScaledFScore import InvalidScalerException, ScaledFScorePresets, ScaledFScorePresetsNeg1To1
from scattertext.termsignificance.LogOddsRatioSmoothed import LogOddsRatioSmoothed
from scattertext.termsignificance.LogOddsRatioInformativeDirichletPiror \
    import LogOddsRatioInformativeDirichletPrior
from scattertext.termsignificance.LogOddsRatioUninformativeDirichletPrior \
    import LogOddsRatioUninformativeDirichletPrior
from scattertext.termsignificance.ScaledFScoreSignificance import ScaledFScoreSignificance
from scattertext.termsignificance.TermSignificance import TermSignificance
from scattertext.viz import VizDataAdapter, ScatterplotStructure, PairPlotFromScatterplotStructure
from scattertext.viz.HTMLSemioticSquareViz import HTMLSemioticSquareViz
from scattertext.semioticsquare.FourSquareAxis import FourSquareAxes
from scattertext.termcompaction.ClassPercentageCompactor import ClassPercentageCompactor
from scattertext.termcompaction.CompactTerms import CompactTerms
from scattertext.termcompaction.PhraseSelector import PhraseSelector
from scattertext.topicmodel.SentencesForTopicModeling import SentencesForTopicModeling
from scattertext.frequencyreaders.DefaultBackgroundFrequencies import DefaultBackgroundFrequencies, \
    BackgroundFrequenciesFromCorpus
from scattertext.termcompaction.DomainCompactor import DomainCompactor
from scattertext.termscoring.ZScores import ZScores
from scattertext.termscoring.RelativeEntropy import RelativeEntropy
from scattertext.categoryprojector.pairplot import produce_pairplot, produce_category_focused_pairplot
from scattertext.categoryprojector.CategoryProjection import CategoryProjection, project_raw_corpus
from scattertext.categoryprojector.CategoryProjectorEvaluator import RipleyKCategoryProjectorEvaluator, \
    EmbeddingsProjectorEvaluator
from scattertext.representations.Doc2VecBuilder import Doc2VecBuilder
from scattertext.ParsedCorpus import ParsedCorpus
from scattertext.distancemeasures.EuclideanDistance import EuclideanDistance
from scattertext.distancemeasures.DistanceMeasureBase import DistanceMeasureBase
from scattertext.termscoring.CredTFIDF import CredTFIDF
from scattertext.representations.CategoryEmbeddings import CategoryEmbeddingsResolver, EmbeddingAligner
from scattertext.features.FeatsFromScoredLexicon import FeatsFromScoredLexicon
from scattertext.features.SpacyEntities import SpacyEntities
from scattertext.diachronic.TimeStructure import TimeStructure
from scattertext.features.PyatePhrases import PyatePhrases
from scattertext.termscoring.DeltaJSDivergence import DeltaJSDivergence
from scattertext.CorpusFromTermFrequencies import CorpusFromTermFrequencies
from scattertext.helpers.MakeUnique import make_unique
from scattertext.viz.TermInfo import get_tooltip_js_function, get_custom_term_info_js_function
from scattertext.CorpusWithoutCategoriesFromParsedDocuments import CorpusWithoutCategoriesFromParsedDocuments
from scattertext.OffsetCorpus import OffsetCorpus
from scattertext.OffsetCorpusFactory import OffsetCorpusFactory
from scattertext.dispersion.Dispersion import Dispersion
from scattertext.features import featoffsets
from scattertext.features.featoffsets.feat_and_offset_getter import FeatAndOffsetGetter
from scattertext.features.featoffsets.token_and_feat_offset_getter import TokenFeatAndOffsetGetter
from scattertext.tokenizers.roberta import RobertaTokenizerWrapper
from scattertext.continuous.sklearnpipeline import RidgeCoefficients
from scattertext.continuous.ungar import UngarCoefficients
from scattertext.features.RegexFeatAndOffsetGetter import RegexFeatAndOffsetGetter
from scattertext.representations.LatentSemanticScaling import latent_semantic_scale_from_word2vec, lss_terms
from scattertext.categorytable import CategoryTableMaker
from scattertext.features.CognitiveDistortionsOffsetGetter import LexiconFeatAndOffsetGetter, \
    COGNITIVE_DISTORTIONS_LEXICON, COGNITIVE_DISTORTIONS_DEFINITIONS
from scattertext.termscoring.LogOddsRatio import LogOddsRatio
from scattertext.termscoring.RankDifferenceScorer import RankDifferenceScorer
from scattertext.categorygrouping.CharacteristicGrouper import CharacteristicGrouper
from scattertext.termscoring.Productivity import ProductivityScorer, whole_corpus_productivity_scores
from scattertext.viz.PyPlotFromScattertextStructure import pyplot_from_scattertext_structure
from scattertext.termscoring.BNSScorer import BNSScorer
from scattertext.features.featoffsets.flexible_ngram_features import PosStopgramFeatures, FlexibleNGramFeatures

PhraseFeatsFromTopicModel = FeatsFromTopicModel  # Ensure backwards compatibility

def cognitive_distortions_offset_getter_factory():
    return LexiconFeatAndOffsetGetter(COGNITIVE_DISTORTIONS_LEXICON, COGNITIVE_DISTORTIONS_DEFINITIONS)


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
                                 match_full_line=False,
                                 use_non_text_features=False,
                                 show_top_terms=True,
                                 show_characteristic=None,
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
                                 x_axis_values_format=None,
                                 y_axis_values_format=None,
                                 color_func=None,
                                 term_scorer=None,
                                 show_axes=True,
                                 show_axes_and_cross_hairs=False,
                                 show_diagonal=False,
                                 use_global_scale=False,
                                 horizontal_line_y_position=None,
                                 vertical_line_x_position=None,
                                 show_cross_axes=True,
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
                                 term_colors=None,
                                 unified_context=False,
                                 show_category_headings=True,
                                 highlight_selected_category=False,
                                 include_term_category_counts=False,
                                 div_name=None,
                                 alternative_term_func=None,
                                 term_metadata=None,
                                 term_metadata_df=None,
                                 max_overlapping=-1,
                                 include_all_contexts=False,
                                 show_corpus_stats=True,
                                 sort_doc_labels_by_name=False,
                                 enable_term_category_description=True,
                                 always_jump=True,
                                 get_custom_term_html=None,
                                 header_names=None,
                                 header_sorting_algos=None,
                                 ignore_categories=False,
                                 d3_color_scale=None,
                                 background_labels=None,
                                 tooltip_columns=None,
                                 tooltip_column_names=None,
                                 term_description_columns=None,
                                 term_description_column_names=None,
                                 term_word_in_term_description='Term',
                                 color_column=None,
                                 color_score_column=None,
                                 label_priority_column=None,
                                 text_color_column=None,
                                 suppress_text_column=None,
                                 background_color=None,
                                 left_list_column=None,
                                 censor_point_column=None,
                                 right_order_column=None,
                                 line_coordinates=None,
                                 subword_encoding=None,
                                 top_terms_length=14,
                                 top_terms_left_buffer=0,
                                 dont_filter=False,
                                 use_offsets=False,
                                 get_column_header_html=None,
                                 show_term_etc=True,
                                 return_data=False,
                                 return_scatterplot_structure=False, ):
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
    metadata : list or function, optional
        list of meta data strings that will be included for each document, if a function, called on corpus
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
    match_full_line : bool, optional
        Has the javascript regex match the full line instead of part of it
    use_non_text_features : bool, optional
        Show non-bag-of-words features (e.g., Empath) instead of text.  False by default.
    show_top_terms : bool, default True
        Show top terms on the left-hand side of the visualization
    show_characteristic: bool, default None
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
      By default, this is `DEFAULT_D3_URL` declared in `ScatterplotStructure`.
    d3_scale_chromatic_url, str, None by default.  Overrides `protocol`.
      URL of d3 scale chromatic, to be inserted into <script src="..."/>
      By default, this is `DEFAULT_D3_SCALE_CHROMATIC` declared in `ScatterplotStructure`.
    pmi_filter_thresold : (DEPRECATED) int, None by default
      DEPRECATED.  Use pmi_threshold_coefficient instead.
    alternative_text_field : str or None, optional
        Field in from dataframe used to make corpus to display in place of parsed text. Only
        can be used if corpus is a ParsedCorpus instance.
    terms_to_include : list or None, optional
        Whitelist of terms to include in visualization.
    semiotic_square : SemioticSquareBase
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
    x_axis_values_format : str, default None
        d3 format of x-axis values
    y_axis_values_format : str, default None
        d3 format of y-axis values
    color_func : str, default None
        Javascript function to control color of a point.  Function takes a parameter
        which is a dictionary entry produced by `ScatterChartExplorer.to_dict` and
        returns a string.
    term_scorer : Object, default None
        In lieu of scores, object with a get_scores(a,b) function that returns a set of scores,
        where a and b are term counts.  Scorer optionally has a get_term_freqs function. Also could be a
        CorpusBasedTermScorer instance.
    show_axes : bool, default True
        Show the ticked axes on the plot.  If false, show inner axes as a crosshair.
    show_axes_and_cross_hairs : bool, default False
        Show both peripheral axis labels and cross axes.
    show_diagonal : bool, default False
        Show a diagonal line leading from the lower-left ot the upper-right; only makes
        sense to use this if use_global_scale is true.
    use_global_scale : bool, default False
        Use same scale for both axes
    vertical_line_x_position : float, default None
    horizontal_line_y_position : float, default None
    show_cross_axes : bool, default True
        If show_axes is False, do we show cross-axes?
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
    term_colors : dict, default None
        Dictionary mapping term to color
    unified_context : bool, default False
        Boolean displays contexts in a single pane as opposed to separate columns.
    show_category_headings : bool, default True
        Show category headings if unified_context is True.
    highlight_selected_category : bool, default False
        Highlight selected category if unified_context is True.
    include_term_category_counts : bool, default False
        Include the termCounts object in the plot definition.
    div_name : str, None by default
        Give the scatterplot div name a non-default value
    alternative_term_func: str, default None
        Javascript function which take a term JSON object and returns a bool.  If the return value is true,
        execute standard term click pipeline. Ex.: `'(function(termDict) {return true;})'`.
    term_metadata : dict, None by default
        Dict mapping terms to dictionaries containing additional information which can be used in the color_func
        or the get_tooltip_content function. These will appear in termDict.etc
    term_metadata_df : pd.DataFrame, None by default
        Dataframe version of term_metadata
    include_all_contexts: bool, default False
        Include all contexts, even non-matching ones, in interface
    max_overlapping: int, default -1
        Number of overlapping terms to dislay. If -1, display all. (default)
    show_corpus_stats: bool, default True
        Show the corpus stats div
    sort_doc_labels_by_name: bool default False
        If unified, sort the document labels by name
    always_jump: bool, default True
        Always jump to term contexts if a term is clicked
    enable_term_category_description: bool, default True
        List term/metadata statistics under category
    get_custom_term_html: str, default None
        Javascript function which displays term summary from term info
    header_names: Dict[str, str], default None
        Dictionary giving names of term lists shown to the right of the plot. Valid keys are
        upper, lower and right.
    header_sorting_algos: Dict[str, str], default None
        Dictionary giving javascript sorting algorithms for panes. Valid keys are upper, lower
        and right. Value is a JS function which takes the "data" object.
    ignore_categories: bool, default False
        Signals the plot shouldn't display category names. Used in single category plots.
    suppress_text_column: str, default None
        Column in term_metadata_df which indicates term should be hidden
    left_list_column: str, default None
        Column in term_metadata_df which should be used for sorting words into upper and lower
        parts of left word-list sections. Highest values in upper, lowest in lower.
    tooltip_columns: List[str]
    tooltip_column_names: Dict[str, str]
    term_description_columns: List[str]
    term_description_column_names: Dict[str]
    term_word_in_term_description: str, default None
    color_column: str, default None:
        column in term_metadata_df which indicates color
    color_score_column: str, default None
        column in term_metadata df; contains value between 0 and 1 which will be used to assign a color
    label_priority_column : str, default None
        Column in term_metadata_df; larger values in the column indicate a term should be labeled first
    censor_point_column : str, default None
        Should we allow labels to be drawn over point?
    right_order_column : str, default None
        Order for right column ("characteristic" by default); largest first
    background_color : str, default None
        Changes document.body's background color to background_color
    line_coordinates : list, default None
        Coordinates for drawing a line under the plot
    subword_encoding : str, default None
        Type of subword encoding to use, None if none, currently supports "RoBERTa"
    top_terms_length : int, default 14
        Number of words to list in most/least associated lists on left-hand side
    top_terms_left_buffer : int, default 0
        Number of pixels left to shift top terms list
    dont_filter : bool, default False
        Don't filter any terms when charting
    get_column_header_html : str, default None
        Javascript function to return html over each column. Matches header
        (Column Name, occurrences per 25k, occs, # occs * 1000/num docs, term info)
    show_term_etc: bool, default True
        Shows list of etc values after clicking term
    use_offsets : bool, default False
        Enable the use of metadata offsets
    return_data : bool default False
        Return a dict containing the output of `ScatterChartExplorer.to_dict` instead of
        an html.
    return_scatterplot_structure : bool, default False
        return ScatterplotStructure instead of html
    Returns
    -------
    str
    html of visualization

    '''
    if singleScoreMode or word_vec_use_p_vals:
        d3_color_scale = 'd3.interpolatePurples'
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
        scores = get_term_scorer_scores(category, corpus, neutral_categories, not_categories, show_neutral, term_ranker,
                                        term_scorer, use_non_text_features)

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
                                                  terms_to_include=terms_to_include,
                                                  dont_filter=dont_filter, )
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
    if term_colors is not None:
        scatter_chart_explorer.inject_term_colors(term_colors)

    if term_metadata_df is not None and term_metadata is not None:
        raise Exception("Both term_metadata_df and term_metadata cannot be values which are not None.")
    if term_metadata_df is not None:
        scatter_chart_explorer.inject_term_metadata_df(term_metadata_df)
    if term_metadata is not None:
        scatter_chart_explorer.inject_term_metadata(term_metadata)
    html_base = None
    if semiotic_square:
        html_base = get_semiotic_square_html(num_terms_semiotic_square,
                                             semiotic_square)
    scatter_chart_data = scatter_chart_explorer.to_dict(
        category=category,
        category_name=category_name,
        not_category_name=not_category_name,
        not_categories=not_categories,
        transform=transform,
        scores=scores,
        max_docs_per_category=max_docs_per_category,
        metadata=metadata if not callable(metadata) else metadata(corpus),
        alternative_text_field=alternative_text_field,
        neutral_category_name=neutral_category_name,
        extra_category_name=extra_category_name,
        neutral_categories=neutral_categories,
        extra_categories=extra_categories,
        background_scorer=characteristic_scorer,
        include_term_category_counts=include_term_category_counts,
        use_offsets=use_offsets,
    )

    if line_coordinates is not None:
        scatter_chart_data['line'] = line_coordinates

    if return_data:
        return scatter_chart_data

    if tooltip_columns is not None:
        assert get_tooltip_content is None
        get_tooltip_content = get_tooltip_js_function(
            term_metadata_df,
            tooltip_column_names,
            tooltip_columns
        )

    if term_description_columns is not None:
        assert get_custom_term_html is None
        get_custom_term_html = get_custom_term_info_js_function(
            term_metadata_df,
            term_description_column_names,
            term_description_columns,
            term_word_in_term_description
        )

    if color_column:
        assert color_func is None
        color_func = '(function(d) {return d.etc["%s"]})' % color_column

    if color_score_column:
        assert color_func is None
        color_func = '(function(d) {return %s(d.etc["%s"])})' % (
            d3_color_scale if d3_color_scale is not None else 'd3.interpolateRdYlBu',
            color_score_column
        )

    if header_sorting_algos is not None:
        assert 'upper' in header_sorting_algos
        assert 'lower' in header_sorting_algos
    if left_list_column is not None:
        assert term_metadata_df is not None
        assert left_list_column in term_metadata_df
        header_sorting_algos = {
            "upper": '((a,b) => b.etc["' + left_list_column + '"] - a.etc["' + left_list_column + '"])',
            "lower": '((a,b) => a.etc["' + left_list_column + '"] - b.etc["' + left_list_column + '"])'
        }
    if right_order_column is not None:
        assert right_order_column in term_metadata_df

    if show_characteristic is None:
        show_characteristic = not (asian_mode or use_non_text_features)

    scatterplot_structure = ScatterplotStructure(
        VizDataAdapter(scatter_chart_data),
        width_in_pixels=width_in_pixels,
        height_in_pixels=height_in_pixels,
        max_snippets=max_snippets,
        color=d3_color_scale,
        grey_zero_scores=gray_zero_scores,
        sort_by_dist=sort_by_dist,
        reverse_sort_scores_for_not_category=reverse_sort_scores_for_not_category,
        use_full_doc=use_full_doc,
        asian_mode=asian_mode,
        match_full_line=match_full_line,
        use_non_text_features=use_non_text_features,
        show_characteristic=show_characteristic,
        word_vec_use_p_vals=word_vec_use_p_vals,
        max_p_val=max_p_val,
        save_svg_button=save_svg_button,
        p_value_colors=p_value_colors,
        x_label=x_label,
        y_label=y_label,
        show_top_terms=show_top_terms,
        show_neutral=show_neutral,
        get_tooltip_content=get_tooltip_content,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        color_func=color_func,
        show_axes=show_axes,
        horizontal_line_y_position=horizontal_line_y_position,
        vertical_line_x_position=vertical_line_x_position,
        show_extra=show_extra,
        do_censor_points=censor_points,
        center_label_over_points=center_label_over_points,
        x_axis_labels=x_axis_labels,
        y_axis_labels=y_axis_labels,
        topic_model_preview_size=topic_model_preview_size,
        vertical_lines=vertical_lines,
        unified_context=unified_context,
        show_category_headings=show_category_headings,
        highlight_selected_category=highlight_selected_category,
        show_cross_axes=show_cross_axes,
        div_name=div_name,
        alternative_term_func=alternative_term_func,
        include_all_contexts=include_all_contexts,
        show_axes_and_cross_hairs=show_axes_and_cross_hairs,
        show_diagonal=show_diagonal,
        use_global_scale=use_global_scale,
        x_axis_values_format=x_axis_values_format,
        y_axis_values_format=y_axis_values_format,
        max_overlapping=max_overlapping,
        show_corpus_stats=show_corpus_stats,
        sort_doc_labels_by_name=sort_doc_labels_by_name,
        enable_term_category_description=enable_term_category_description,
        always_jump=always_jump,
        get_custom_term_html=get_custom_term_html,
        header_names=header_names,
        header_sorting_algos=header_sorting_algos,
        ignore_categories=ignore_categories,
        background_labels=background_labels,
        label_priority_column=label_priority_column,
        text_color_column=text_color_column,
        suppress_text_column=suppress_text_column,
        background_color=background_color,
        censor_point_column=censor_point_column,
        right_order_column=right_order_column,
        subword_encoding=subword_encoding,
        top_terms_length=top_terms_length,
        top_terms_left_buffer=top_terms_left_buffer,
        get_column_header_html=get_column_header_html,
        term_word=term_word_in_term_description,
        show_term_etc=show_term_etc
    )

    if return_scatterplot_structure:
        return scatterplot_structure

    return (BasicHTMLFromScatterplotStructure(scatterplot_structure)
            .to_html(protocol=protocol,
                     d3_url=d3_url,
                     d3_scale_chromatic_url=d3_scale_chromatic_url,
                     html_base=html_base))


def get_term_scorer_scores(category, corpus, neutral_categories, not_categories, show_neutral,
                           term_ranker, term_scorer, use_non_text_features):
    tdf = corpus.apply_ranker(term_ranker, use_non_text_features)

    cat_freqs = tdf[category + ' freq']
    if not_categories:
        not_cat_freqs = tdf[[c + ' freq' for c in not_categories]].sum(axis=1)
    else:
        not_cat_freqs = tdf.sum(axis=1) - tdf[category + ' freq']
    if isinstance(term_scorer, CorpusBasedTermScorer) and not term_scorer.is_category_name_set():
        if show_neutral:
            term_scorer = term_scorer.set_categories(category, not_categories, neutral_categories)
        else:
            term_scorer = term_scorer.set_categories(category, not_categories)
    return term_scorer.get_scores(cat_freqs, not_cat_freqs)


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

    scatterplot_structure = ScatterplotStructure(VizDataAdapter(scatter_chart_data), width_in_pixels, height_in_pixels)
    return BasicHTMLFromScatterplotStructure(scatterplot_structure).to_html(protocol=protocol)


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
    '''

    :param num_terms_semiotic_square: int
    :param semiotic_square: SemioticSquare
    :return: str
    '''
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
        E.g., spacy.load('en_core_web_sm'), whitespace_nlp, etc...
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
        nlp = spacy.load('en_core_web_sm')

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
                               grey_threshold=0,
                               y_axis_values=None,
                               frequency_transform=lambda x: scale(np.log(x) - np.log(1)),
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
    frequency_transfom : lambda, default lambda x: scale(np.log(x) - np.log(1))
        Takes a vector of frequencies and returns their x-axis scale.
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
    frequencies_log_scaled = frequency_transform(freqs)  # scale(np.log(freqs) - np.log(1))

    if 'scores' not in kwargs:
        kwargs['scores'] = get_term_scorer_scores(category,
                                                  corpus,
                                                  kwargs.get('neutral_categories', False),
                                                  not_categories,
                                                  kwargs.get('show_neutral', False),
                                                  term_ranker,
                                                  term_scorer,
                                                  kwargs.get('use_non_text_features', False))

    def y_axis_rescale(coords):
        return ((coords - 0.5) / (np.abs(coords - 0.5).max()) + 1) / 2

    # from https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
    def round_to_1(x):
        if x == 0:
            return 0
        return round(x, -int(np.floor(np.log10(abs(x)))))

    if y_axis_values is None:
        max_score = np.floor(np.max(kwargs['scores']) * 100) / 100
        min_score = np.ceil(np.min(kwargs['scores']) * 100) / 100
        if min_score < 0 and max_score > 0:
            central = 0
        else:
            central = 0.5
        y_axis_values = [x for x in [min_score, central, max_score]
                         if x >= min_score and x <= max_score]
    scores_scaled_for_charting = scale_neg_1_to_1_with_zero_mean_abs_max(kwargs['scores'])
    if use_term_significance:
        kwargs['term_significance'] = term_scorer

    kwargs['y_label'] = kwargs.get('y_label', term_scorer.get_name())

    kwargs['color_func'] = kwargs.get('color_func', '''(function(d) {
	return (Math.abs(d.os) < %s) 
	 ? d3.interpolate(d3.rgb(230, 230, 230), d3.rgb(130, 130, 130))(Math.abs(d.os)/%s) 
	 : d3.interpolateRdYlBu(d.y);
	})''' % (grey_threshold, grey_threshold))

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
                                        not_categories=not_categories,
                                        x_label=kwargs.get('x_label', 'Log Frequency'),
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
        Word embeddings.  If None (default), will train them using word2vec Model
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
                         x_label='',
                         y_label='',
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
        if kwargs.get('use_non_text_features', False):
            assert set(projection.index) == set(corpus.get_metadata())
        else:
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
        y_label=y_label,
        x_label=x_label,
        show_axes=show_axes,
        horizontal_line_y_position=kwargs.get('horizontal_line_y_position', 0),
        vertical_line_x_position=kwargs.get('vertical_line_x_position', 0),
        **kwargs
    )
    return html


produce_fixed_explorer = produce_pca_explorer


def produce_characteristic_explorer(corpus,
                                    category,
                                    category_name=None,
                                    not_category_name=None,
                                    not_categories=None,
                                    characteristic_scorer=DenseRankCharacteristicness(),
                                    term_ranker=termranking.AbsoluteFrequencyRanker,
                                    term_scorer=RankDifference(),
                                    x_label='Characteristic to Corpus',
                                    y_label=None,
                                    y_axis_labels=None,
                                    scores=None,
                                    vertical_lines=None,
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
    corpus = corpus.remove_terms(
        set(corpus.get_terms()) - set(characteristic_scores.index)
    )
    characteristic_scores = characteristic_scores.loc[corpus.get_terms()]
    term_freq_df = term_ranker(corpus).get_ranks()
    scores = term_scorer.get_scores(
        term_freq_df[category + ' freq'],
        term_freq_df[[c + ' freq' for c in not_categories]].sum(axis=1)
    ) if scores is None else scores
    scores_scaled_for_charting = scale_neg_1_to_1_with_zero_mean_abs_max(scores)
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
        y_axis_labels=['More ' + not_category_name, 'Even', 'More ' + category_name
                       ] if y_axis_labels is None else y_axis_labels,
        x_label=x_label,
        y_label=term_scorer.get_name() if y_label is None else y_label,
        vertical_lines=[] if vertical_lines is None else vertical_lines,
        characteristic_scorer=characteristic_scorer,
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


def pick_color(x_pval, y_pval, x_d, y_d):
    if x_d > 0.2 and y_d > 0.2:
        return 'fc00a0'
    if x_d > 0.2 or y_d > 0.2:
        return 'a300fc'
    if x_pval < 0.001 and y_pval < 0.001:
        return 'blue'
    if x_pval < 0.001 or y_pval < 0.001:
        return '00befc'
    else:
        return 'CCCCCC'


def produce_two_axis_plot(corpus,
                          x_score_df,
                          y_score_df,
                          x_label,
                          y_label,
                          statistic_column='cohens_d',
                          p_value_column='cohens_d_p',
                          statistic_name='d',
                          use_non_text_features=False,
                          pick_color=pick_color,
                          axis_scaler=scale_neg_1_to_1_with_zero_mean,
                          distance_measure=EuclideanDistance,
                          semiotic_square_labels=None,
                          x_tooltip_label=None,
                          y_tooltip_label=None,
                          **kwargs):
    '''

    :param corpus: Corpus
    :param x_score_df: pd.DataFrame, contains effect_size_column, p_value_column. outputted by CohensD
    :param y_score_df: pd.DataFrame, contains effect_size_column, p_value_column. outputted by CohensD
    :param x_label: str
    :param y_label: str
    :param statistic_column: str, column in x_score_df, y_score_df giving statistics, default cohens_d
    :param p_value_column: str, column in x_score_df, y_score_df giving effect sizes, default cohens_d_p
    :param statistic_name: str, column which corresponds to statistic name, defauld d
    :param use_non_text_features: bool, default True
    :param pick_color: func, returns color, default is pick_color
    :param axis_scaler: func, scaler default is scale_neg_1_to_1_with_zero_mean
    :param distance_measure: DistanceMeasureBase, default EuclideanDistance
        This is how parts of the square are populated
    :param semiotic_square_labels: dict, semiotic square position labels
    :param x_tooltip_label: str, if None, x_label
    :param y_tooltip_label: str, if None, y_label
    :param kwargs: dict, other arguments
    :return: str, html
    '''

    if use_non_text_features:
        terms = corpus.get_metadata()
    else:
        terms = corpus.get_terms()

    axes = pd.DataFrame({'x': x_score_df[statistic_column],
                         'y': y_score_df[statistic_column]}).loc[terms]
    merged_scores = pd.merge(x_score_df, y_score_df, left_index=True, right_index=True).loc[terms]

    x_tooltip_label = x_label if x_tooltip_label is None else x_tooltip_label
    y_tooltip_label = y_label if y_tooltip_label is None else y_tooltip_label

    def generate_term_metadata(term_struct):
        if p_value_column + '_corr_x' in term_struct:
            x_p = term_struct[p_value_column + '_corr_x']
        elif p_value_column + '_x' in term_struct:
            x_p = term_struct[p_value_column + '_x']
        else:
            x_p = None
        if p_value_column + '_corr_y' in term_struct:
            y_p = term_struct[p_value_column + '_corr_y']
        elif p_value_column + '_y' in term_struct:
            y_p = term_struct[p_value_column + '_y']
        else:
            y_p = None
        if x_p is not None:
            x_p = min(x_p, 1. - x_p)
        if y_p is not None:
            y_p = min(y_p, 1. - y_p)

        x_d = term_struct[statistic_column + '_x']
        y_d = term_struct[statistic_column + '_y']

        tooltip = '%s: %s: %0.3f' % (x_tooltip_label, statistic_name, x_d)
        if x_p is not None:
            tooltip += '; p: %0.4f' % x_p
        tooltip += '<br/>'
        tooltip += '%s: %s: %0.3f' % (y_tooltip_label, statistic_name, y_d)
        if y_p is not None:
            tooltip += '; p: %0.4f' % y_p

        return {'tooltip': tooltip, 'color': pick_color(x_p, y_p, np.abs(x_d), np.abs(y_d))}

    explanations = merged_scores.apply(generate_term_metadata, axis=1)

    semiotic_square = SemioticSquareFromAxes(corpus,
                                             axes,
                                             x_axis_name=x_label,
                                             y_axis_name=y_label,
                                             labels=semiotic_square_labels,
                                             distance_measure=distance_measure)

    get_tooltip_content = kwargs.get('get_tooltip_content',
                                     '''(function(d) {return d.term + "<br/> " + d.etc.tooltip})''')
    color_func = kwargs.get('color_func', '''(function(d) {return d.etc.color})''')

    html = produce_scattertext_explorer(corpus,
                                        category=corpus.get_categories()[0],
                                        sort_by_dist=False,
                                        x_coords=axis_scaler(axes['x']),
                                        y_coords=axis_scaler(axes['y']),
                                        original_x=axes['x'],
                                        original_y=axes['y'],
                                        show_characteristic=False,
                                        show_top_terms=False,
                                        show_category_headings=True,
                                        x_label=x_label,
                                        y_label=y_label,
                                        semiotic_square=semiotic_square,
                                        get_tooltip_content=get_tooltip_content,
                                        x_axis_values=None,
                                        y_axis_values=None,
                                        unified_context=True,
                                        color_func=color_func,
                                        show_axes=False,
                                        term_metadata=explanations.to_dict(),
                                        use_non_text_features=use_non_text_features,
                                        **kwargs)
    return html


def produce_scattertext_digraph(
        df,
        text_col,
        source_col,
        dest_col,
        source_name='Source',
        dest_name='Destination',
        graph_width=500,
        graph_height=500,
        metadata_func=None,
        enable_pan_and_zoom=True,
        engine='dot',
        graph_params=None,
        node_params=None,
        **kwargs
):
    '''

    :param df: pd.DataFrame
    :param text_col: str
    :param source_col: str
    :param dest_col: str
    :param source_name: str
    :param dest_name: str
    :param graph_width: int
    :param graph_height: int
    :param metadata_func: lambda
    :param enable_pan_and_zoom: bool
    :param engine: str, The graphviz engine (e.g., dot or neat)
    :param graph_params dict or None, graph parameters in graph viz
    :param node_params dict or None, node parameters in graph viz
    :param kwargs: dicdt
    :return:
    '''
    graph_df = pd.concat([
        df.assign(
            __text=lambda df: df[source_col],
            __alttext=lambda df: df[text_col],
            __category='source'
        ),
        df.assign(
            __text=lambda df: df[dest_col],
            __alttext=lambda df: df[text_col],
            __category='target'
        )
    ])

    corpus = CorpusFromParsedDocuments(
        graph_df,
        category_col='__category',
        parsed_col='__text',
        feats_from_spacy_doc=UseFullDocAsMetadata()
    ).build()

    edges = (corpus.get_df()[[source_col, dest_col]]
             .rename(columns={source_col: 'source', dest_col: 'target'})
             .drop_duplicates())

    component_graph = SimpleDiGraph(edges).make_component_digraph(
        graph_params=graph_params,
        node_params=node_params
    )

    graph_renderer = ComponentDiGraphHTMLRenderer(
        component_graph,
        height=graph_height,
        width=graph_width,
        enable_pan_and_zoom=enable_pan_and_zoom,
        engine=engine,
    )

    alternative_term_func = '''(function(termDict) {
        document.querySelectorAll(".dotgraph").forEach(svg => svg.style.display = 'none');
        showTermGraph(termDict['term']);
        return true;
    })'''

    scatterplot_structure = produce_scattertext_explorer(
        corpus,
        category='source',
        category_name=source_name,
        not_category_name=dest_name,
        minimum_term_frequency=0,
        pmi_threshold_coefficient=0,
        alternative_text_field='__alttext',
        use_non_text_features=True,
        transform=dense_rank,
        metadata=corpus.get_df().apply(metadata_func, axis=1) if metadata_func else None,
        return_scatterplot_structure=True,
        width_in_pixels=kwargs.get('width_in_pixels', 700),
        max_overlapping=kwargs.get('max_overlapping', 3),
        color_func=kwargs.get('color_func', '(function(x) {return "#5555FF"})'),
        alternative_term_func=alternative_term_func,
        **kwargs
    )

    html = GraphStructure(
        scatterplot_structure,
        graph_renderer=graph_renderer
    ).to_html()

    return html


def dataframe_scattertext(
        corpus,
        plot_df,
        **kwargs
):
    assert 'X' in plot_df
    assert 'Y' in plot_df
    if 'Xpos' not in plot_df:
        plot_df['Xpos'] = Scalers.scale(plot_df['X'])
    if 'Ypos' not in plot_df:
        plot_df['Ypos'] = Scalers.scale(plot_df['Y'])

    assert len(plot_df) > 0

    if 'term_description_columns' not in kwargs:
        kwargs['term_description_columns'] = [x for x in plot_df.columns if x not in
                                              ['X', 'Y', 'Xpos', 'Ypos']]

    if 'tooltip_columns' not in kwargs:
        kwargs['tooltip_columns'] = ['Xpos', 'Ypos']
        kwargs['tooltip_column_names'] = {'Xpos': kwargs.get('x_label', 'X'), 'Ypos': kwargs.get('y_label', 'Y')}

    kwargs.setdefault('metadata', None),
    kwargs.setdefault('scores', plot_df['Score'] if 'Score' in plot_df else 0),
    kwargs.setdefault('minimum_term_frequency', 0)
    kwargs.setdefault('pmi_threshold_coefficient', 0)
    kwargs.setdefault('category', corpus.get_categories()[0])
    kwargs.setdefault('original_x', plot_df['X'].values)
    kwargs.setdefault('original_y', plot_df['Y'].values)
    kwargs.setdefault('x_coords', plot_df['Xpos'].values)
    kwargs.setdefault('y_coords', plot_df['Ypos'].values)
    kwargs.setdefault('use_global_scale', True)
    kwargs.setdefault('ignore_categories', True)
    kwargs.setdefault('unified_context', kwargs['ignore_categories'])
    kwargs.setdefault('show_axes_and_cross_hairs', 0)
    kwargs.setdefault('show_top_terms', False)
    kwargs.setdefault('x_label', 'X')
    kwargs.setdefault('y_label', 'Y')
    return produce_scattertext_explorer(
        corpus,
        term_metadata_df=plot_df,
        **kwargs
    )


class TableStructure(GraphStructure):
    def __init__(self,
                 scatterplot_structure,
                 graph_renderer,
                 **kwargs):
        kwargs.setdefault('template_file_name', 'table_plot.html')
        GraphStructure.__init__(self, scatterplot_structure, graph_renderer, **kwargs)

    def get_font_import(self):
        return ''

    def get_zoom_script_import(self):
        return ''


def produce_scattertext_table(
        corpus,
        num_rows=10,
        use_non_text_features=False,
        plot_width=500,
        plot_height=700,
        category_order=None,
        d3_url_struct=D3URLs(),
        **kwargs
):
    '''

    :param df: pd.DataFrame
    :param text_col: str
    :param source_col: str
    :param dest_col: str
    :param source_name: str
    :param dest_name: str
    :param plot_width: int
    :param plot_height: int
    :param enable_pan_and_zoom: bool
    :param engine: str, The graphviz engine (e.g., dot or neat)
    :param graph_params dict or None, graph parameters in graph viz
    :param node_params dict or None, node parameters in graph viz
    :param category_order list or None, names of categories to show in order
    :param kwargs: dict
    :return: str
    '''

    alternative_term_func = '''(function(termDict) {
       //document.querySelectorAll(".dotgraph").forEach(svg => svg.style.display = 'none');
       //showTermGraph(termDict['term']);
       //alert(termDict['term'])
       return true;
    })'''

    graph_renderer = CategoryTableMaker(
        corpus=corpus,
        num_rows=num_rows,
        use_metadata=use_non_text_features,
        category_order=category_order
    )

    dispersion = Dispersion(
        corpus, use_categories=True, use_metadata=use_non_text_features
    )

    adjusted_dispersion = dispersion.get_adjusted_metric(
        dispersion.da(),
        dispersion.get_frequency()
    )

    plot_df = pd.DataFrame().assign(
        X=dispersion.get_frequency(),
        Frequency=lambda df: df.X,
        Xpos=lambda df: Scalers.dense_rank(df.X),
        Y=lambda df: adjusted_dispersion,
        AdjustedDA=lambda df: df.Y,
        Ypos=lambda df: Scalers.scale_neg_1_to_1_with_zero_mean(df.Y),
        ColorScore=lambda df: Scalers.scale_neg_1_to_1_with_zero_mean(df.Y),
        term=dispersion.get_names()
    ).set_index('term')

    line_df = pd.DataFrame({
        'x': plot_df.Xpos.values,
        'y': 0.5,
    }).sort_values(by='x')
    kwargs.setdefault('top_terms_left_buffer', 10)
    scatterplot_structure = dataframe_scattertext(
        corpus,
        plot_df=plot_df,
        ignore_categories=False,
        unified_context=kwargs.get('unified_context', True),
        x_label='Frequency Rank',
        y_label='Frequency-adjusted DA',
        y_axis_labels=['More Concentrated', 'Medium', 'More Dispersion'],
        color_score_column='ColorScore',
        tooltip_columns=['Frequency', 'AdjustedDA'],
        header_names={'upper': 'Dispersed', 'lower': 'Concentrated'},
        left_list_column='AdjustedDA',
        line_coordinates=line_df.to_dict('records'),
        use_non_text_features=use_non_text_features,
        return_scatterplot_structure=True,
        width_in_pixels=plot_width,
        height_in_pixels=plot_height,
        d3_url=d3_url_struct.get_d3_url(),
        d3_scale_chromatic_url=d3_url_struct.get_d3_scale_chromatic_url(),
        # alternative_term_func=alternative_term_func,
        **kwargs
    )

    html = TableStructure(
        scatterplot_structure,
        graph_renderer=graph_renderer,
        d3_url_struct=d3_url_struct
    ).to_html()

    return html


def produce_scattertext_pyplot(
        scatterplot_structure,
        figsize=(15, 7),
        textsize=7,
        distance_margin_fraction=0.009,
        scatter_size=5,
        cmap="RdYlBu",
        sample=0,
        xlabel=None,
        ylabel=None,
        dpi=300,
        draw_lines=False,
        linecolor="k",
        draw_all=False,
        nbr_candidates=0,
):
    '''
    Parameters
    ----------
    scatterplot_structure : ScatterplotStructure
    figsize : Tuple[int,int]
        Size of ouput pyplot figure
    textsize : int
        Size of text terms in plot
    distance_margin_fraction : float
        Fraction of the 2d space to use as margins for text bboxes
    scatter_size : int
        Size of scatter disks
    cmap : str
        Matplotlib compatible colormap
    sample : int
        if >0 samples a subset from the scatterplot_structure, used for testing
    xlabel : str
        Overrides label from scatterplot_structure
    ylabel : str
        Overrides label from scatterplot_structure
    dpi : int
        Pyplot figure resolution

    Returns
    -------
    matplotlib.figure.Figure
    matplotlib figure that can be used with plt.show() or plt.savefig()

    '''
    return pyplot_from_scattertext_structure(
        scatterplot_structure,
        figsize=figsize,
        textsize=textsize,
        distance_margin_fraction=distance_margin_fraction,
        scatter_size=scatter_size,
        cmap=cmap,
        sample=sample,
        xlabel=xlabel,
        ylabel=ylabel,
        dpi=dpi,
        draw_lines=draw_lines,
        linecolor=linecolor,
        draw_all=draw_all,
        nbr_candidates=nbr_candidates,
    )
