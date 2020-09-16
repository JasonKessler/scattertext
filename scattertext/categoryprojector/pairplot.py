import numpy as np
from scipy.stats import rankdata, pearsonr
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.metrics.pairwise import cosine_distances

from scattertext.Scalers import stretch_0_to_1, dense_rank
from scattertext.termcompaction.AssociationCompactor import AssociationCompactor
from scattertext.termscoring.RankDifference import RankDifference
from scattertext.viz import ScatterplotStructure, VizDataAdapter
from scattertext.viz.PairPlotFromScattertextStructure import PairPlotFromScatterplotStructure
from scattertext.ScatterChartExplorer import ScatterChartExplorer
from scattertext.categoryprojector.CategoryProjector import CategoryProjector
from scattertext.viz.BasicHTMLFromScatterplotStructure import D3URLs
from scattertext.Scalers import scale_neg_1_to_1_with_zero_mean
from scattertext.termranking.AbsoluteFrequencyRanker import AbsoluteFrequencyRanker


def produce_category_focused_pairplot(corpus,
                                      category,
                                      category_projector=CategoryProjector(projector=TruncatedSVD(20)),
                                      category_projection=None,
                                      **kwargs):
    '''
    Produces a pair-plot which is focused on a single category.

    :param corpus: TermDocMatrix
    :param category: str, name of a category in the corpus
    :param category_projector: CategoryProjector, a factor analysis of the category/feature vector
    :param category_projection: CategoryProjection, None by default. If present, overrides category projector
    :param kwargs: remaining kwargs for produce_pairplot
    :return: str, HTML
    '''

    category_num = corpus.get_categories().index(category)

    uncorrelated_components_projection = (category_projector.project(corpus)
                                          if category_projection is None
                                          else category_projection)

    distances = cosine_distances(uncorrelated_components_projection.get_category_embeddings().T)

    similarity_to_category_scores = -2 * (rankdata(distances[category_num]) - 0.5)

    uncorrelated_components = uncorrelated_components_projection.get_projection()

    least_correlated_dimension = min([(np.abs(pearsonr(similarity_to_category_scores,
                                                       uncorrelated_components.T[i])[0]), i)]
                                     for i in range(uncorrelated_components.shape[1]))[0][1]

    projection_to_plot = np.array([uncorrelated_components.T[least_correlated_dimension],
                                   similarity_to_category_scores]).T

    return produce_pairplot(
        corpus,
        initial_category=category,
        category_projection=uncorrelated_components_projection.use_alternate_projection(projection_to_plot),
        category_focused=True,
        **kwargs
    )


def produce_pairplot(corpus,
                     asian_mode=False,
                     category_width_in_pixels=500,
                     category_height_in_pixels=700,
                     term_width_in_pixels=500,
                     term_height_in_pixels=700,
                     terms_to_show=3000,
                     scaler=scale_neg_1_to_1_with_zero_mean,
                     term_ranker=AbsoluteFrequencyRanker,
                     use_metadata=False,
                     category_projector=CategoryProjector(),
                     category_projection=None,
                     topic_model_term_lists=None,
                     topic_model_preview_size=10,
                     metadata_descriptions=None,
                     initial_category=None,
                     x_dim=0,
                     y_dim=1,
                     show_halo=True,
                     num_terms_in_halo=5,
                     category_color_func='(function(x) {return "#5555FF"})',
                     protocol='https',
                     d3_url_struct=D3URLs(),
                     category_focused=False,
                     verbose=False,
                     use_full_doc=True,
                     default_to_term_comparison=True,
                     category_x_label='',
                     category_y_label='',
                     category_show_axes_and_cross_hairs=False,
                     highlight_selected_category=True,
                     term_x_label=None,  # used if default_to_term_comparison
                     term_y_label=None,  # used if default_to_term_comparison
                     wordfish_style=False,
                     **kwargs):
    if category_projection is None:
        if use_metadata:
            category_projection = category_projector.project_with_metadata(corpus, x_dim=x_dim, y_dim=y_dim)
        else:
            category_projection = category_projector.project(corpus, x_dim=x_dim, y_dim=y_dim)

    if initial_category is None:
        initial_category = corpus.get_categories()[0]
    category_scatter_chart_explorer = _get_category_scatter_chart_explorer(
        category_projection, scaler, term_ranker, verbose
    )
    category_scatter_chart_data = category_scatter_chart_explorer.to_dict(
        category=initial_category,
        max_docs_per_category=0,
    )

    category_tooltip_func = '(function(d) {return d.term})'

    initial_category_idx = corpus.get_categories().index(initial_category)
    term_plot_change_func = _get_term_plot_change_js_func(wordfish_style, category_focused, initial_category_idx)

    category_scatterplot_structure = ScatterplotStructure(
        VizDataAdapter(category_scatter_chart_data),
        width_in_pixels=category_width_in_pixels,
        height_in_pixels=category_height_in_pixels,
        asian_mode=asian_mode,
        use_non_text_features=True,
        show_characteristic=False,
        x_label=category_x_label,
        y_label=category_y_label,
        show_axes_and_cross_hairs=category_show_axes_and_cross_hairs,
        full_data='getCategoryDataAndInfo()',
        show_top_terms=False,
        get_tooltip_content=category_tooltip_func,
        color_func=category_color_func,
        show_axes=False,
        horizontal_line_y_position=0,
        vertical_line_x_position=0,
        unified_context=True,
        show_category_headings=False,
        show_cross_axes=True,
        div_name='cat-plot',
        alternative_term_func=term_plot_change_func,
        highlight_selected_category=highlight_selected_category
    )
    compacted_corpus = AssociationCompactor(terms_to_show,
                                            use_non_text_features=use_metadata).compact(corpus)
    terms_to_hide = set(corpus.get_terms()) - set(compacted_corpus.get_terms())
    if verbose:
        print('num terms to hide', len(terms_to_hide))
        print('num terms to show', compacted_corpus.get_num_terms())

    term_scatter_chart_explorer = ScatterChartExplorer(
        category_projection.get_corpus(),
        minimum_term_frequency=0,
        minimum_not_category_term_frequency=0,
        pmi_threshold_coefficient=0,
        term_ranker=term_ranker,
        use_non_text_features=use_metadata,
        score_transform=stretch_0_to_1,
        verbose=verbose
    ).hide_terms(terms_to_hide)

    if default_to_term_comparison:
        if topic_model_term_lists is not None:
            term_scatter_chart_explorer.inject_metadata_term_lists(topic_model_term_lists)
        if metadata_descriptions is not None:
            term_scatter_chart_explorer.inject_metadata_descriptions(metadata_descriptions)

        if use_metadata:
            tdf = corpus.get_metadata_freq_df('')
        else:
            tdf = corpus.get_term_freq_df('')

        scores = RankDifference().get_scores(
            tdf[initial_category], tdf[[c for c in corpus.get_categories() if c != initial_category]].sum(axis=1)
        )

        term_scatter_chart_data = term_scatter_chart_explorer.to_dict(
            category=initial_category,
            scores=scores,
            include_term_category_counts=True,
            transform=dense_rank,
            **kwargs
        )
        y_label = initial_category,
        x_label = 'Not ' + initial_category,
        color_func = None
        show_top_terms = True
        show_axes = False
    else:
        term_projection = category_projection.get_term_projection()
        original_x = term_projection['x']
        original_y = term_projection['y']
        x_coords = scaler(term_projection['x'])
        y_coords = scaler(term_projection['y'])
        x_label = term_x_label if term_x_label is not None else ''
        y_label = term_y_label if term_y_label is not None else ''
        show_axes = True
        horizontal_line_y_position = 0
        vertical_line_x_position = 0
        term_scatter_chart_explorer.inject_coordinates(x_coords,
                                                       y_coords,
                                                       original_x=original_x,
                                                       original_y=original_y)

        if topic_model_term_lists is not None:
            term_scatter_chart_explorer.inject_metadata_term_lists(topic_model_term_lists)
        if metadata_descriptions is not None:
            term_scatter_chart_explorer.inject_metadata_descriptions(metadata_descriptions)
        term_scatter_chart_data = term_scatter_chart_explorer.to_dict(
            category=initial_category,
            category_name=initial_category,
            include_term_category_counts=True,
            # transform=dense_rank,
        )
        color_func = '(function(x) {return "#5555FF"})'
        show_top_terms = False

    term_scatterplot_structure = ScatterplotStructure(
        VizDataAdapter(term_scatter_chart_data),
        width_in_pixels=term_width_in_pixels,
        height_in_pixels=term_height_in_pixels,
        use_full_doc=use_metadata or use_full_doc, asian_mode=asian_mode,
        use_non_text_features=use_metadata, show_characteristic=False,
        x_label=x_label,
        y_label=y_label,
        full_data='getTermDataAndInfo()',
        show_top_terms=show_top_terms,
        get_tooltip_content=None,
        color_func=color_func,
        # horizontal_line_y_position=0,
        # vertical_line_x_position=0,
        show_axes=show_axes,
        topic_model_preview_size=topic_model_preview_size,
        show_category_headings=False,
        div_name='d3-div-1',
        unified_context=True,
        highlight_selected_category=highlight_selected_category
    )
    return PairPlotFromScatterplotStructure(
        category_scatterplot_structure,
        term_scatterplot_structure,
        category_projection,
        category_width_in_pixels,
        category_height_in_pixels,
        num_terms=num_terms_in_halo,
        show_halo=show_halo,
        d3_url_struct=d3_url_struct,
        x_dim=x_dim,
        y_dim=y_dim,
        protocol=protocol
    ).to_html()


def _get_category_scatter_chart_explorer(category_projection, scaler, term_ranker, verbose):
    category_scatter_chart_explorer = ScatterChartExplorer(
        category_projection.get_corpus(),
        minimum_term_frequency=0,
        minimum_not_category_term_frequency=0,
        pmi_threshold_coefficient=0,
        filter_unigrams=False,
        jitter=0,
        max_terms=None,
        # term_ranker=term_ranker,
        use_non_text_features=True,
        term_significance=None,
        terms_to_include=None,
        verbose=verbose
    )
    proj_df = category_projection.get_pandas_projection()
    category_scatter_chart_explorer.inject_coordinates(
        x_coords=scaler(proj_df['x']),
        y_coords=scaler(proj_df['y']),
        original_x=proj_df['x'],
        original_y=proj_df['y']
    )
    return category_scatter_chart_explorer


def _get_term_plot_change_js_func(wordfish_style, category_focused, initial_category_idx):
    if wordfish_style:
        return '(function (termInfo) {termPlotInterface.yAxisLogCounts(termInfo.term); return false;})'
    if category_focused:
        return '(function (termInfo) {termPlotInterface.drawCategoryAssociation(%s, termInfo.i); return false;})' % (
            initial_category_idx
        )
    return '(function (termInfo) {termPlotInterface.drawCategoryAssociation(termInfo.i); return false;})'
