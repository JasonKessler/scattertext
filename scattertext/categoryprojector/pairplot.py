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
                     **kwargs):
    if category_projection is None:
        if use_metadata:
            category_projection = category_projector.project_with_metadata(corpus, x_dim=x_dim, y_dim=y_dim)
            term_projection = category_projector
        else:
            category_projection = category_projector.project(corpus, x_dim=x_dim, y_dim=y_dim)

    if initial_category is None:
        initial_category = corpus.get_categories()[0]

    category_scatter_chart_explorer = ScatterChartExplorer(category_projection.category_corpus,
                                                           minimum_term_frequency=0,
                                                           minimum_not_category_term_frequency=0,
                                                           pmi_threshold_coefficient=0,
                                                           filter_unigrams=False,
                                                           jitter=0,
                                                           max_terms=None,
                                                           term_ranker=term_ranker,
                                                           use_non_text_features=True,
                                                           term_significance=None,
                                                           terms_to_include=None)
    proj_df = category_projection.get_pandas_projection()
    category_scatter_chart_explorer.inject_coordinates(x_coords=scaler(proj_df['x']),
                                                       y_coords=scaler(proj_df['y']),
                                                       original_x=proj_df['x'],
                                                       original_y=proj_df['y'])
    category_scatter_chart_data = category_scatter_chart_explorer.to_dict(
        category=initial_category, max_docs_per_category=0,
    )

    category_tooltip_func = '(function(d) {return d.term})'

    category_scatterplot_structure = ScatterplotStructure(
        VizDataAdapter(category_scatter_chart_data),
        width_in_pixels=category_width_in_pixels,
        height_in_pixels=category_height_in_pixels,
        asian_mode=asian_mode,
        use_non_text_features=True,
        show_top_terms=False,
        show_characteristic=False,
        get_tooltip_content=category_tooltip_func,
        color_func=category_color_func,
        show_axes=False,
        unified_context=True,
        show_category_headings=False,
        show_cross_axes=True,
        horizontal_line_y_position=0,
        vertical_line_x_position=0,
        y_label='',
        x_label='',
        full_data='getCategoryDataAndInfo()',
        alternative_term_func='(function (termInfo) {termPlotInterface.drawCategoryAssociation(termInfo.i); return false;})',
        div_name='cat-plot'
    )

    compacted_corpus = AssociationCompactor(terms_to_show).compact(corpus)
    terms_to_hide = set(corpus.get_terms()) - set(compacted_corpus.get_terms())
    print('num terms to hide', len(terms_to_hide))
    print('num terms to show', compacted_corpus.get_num_terms())

    term_scatter_chart_explorer = ScatterChartExplorer(
        corpus,
        minimum_term_frequency=0,
        minimum_not_category_term_frequency=0,
        pmi_threshold_coefficient=0,
        term_ranker=term_ranker,
        use_non_text_features=use_metadata,
        score_transform=stretch_0_to_1,
    ).hide_terms(terms_to_hide)

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

    term_scatterplot_structure = ScatterplotStructure(
        VizDataAdapter(term_scatter_chart_data),
        width_in_pixels=term_width_in_pixels,
        height_in_pixels=term_height_in_pixels,
        asian_mode=asian_mode,
        use_non_text_features=use_metadata,
        show_top_terms=True,
        show_characteristic=False,
        get_tooltip_content=None,
        show_category_headings=False,
        use_full_doc=use_metadata,
        horizontal_line_y_position=0,
        vertical_line_x_position=0,
        topic_model_preview_size=topic_model_preview_size,
        y_label=initial_category,
        x_label='Not ' + initial_category,
        full_data='getTermDataAndInfo()',
        div_name='d3-div-1',
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