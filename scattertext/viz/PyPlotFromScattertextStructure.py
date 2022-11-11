import pandas as pd
import random


def pyplot_from_scattertext_structure(
    scatterplot_structure,
    figsize,
    textsize,
    distance_margin_fraction,
    scatter_size,
    cmap,
    sample,
    xlabel,
    ylabel,
    dpi,
    draw_lines,
    linecolor,
    draw_all,
    nbr_candidates,
):
    """
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
        Matplotlib compatible colormap string
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

    """
    try:
        import matplotlib.pyplot as plt
        import textalloc as ta
    except:
        raise Exception("Ensure that the packages textalloc==0.0.3 and matplotlib>=3.6.0 have been installed.")

    # Extract the data
    if sample > 0:
        subset = random.sample(
            scatterplot_structure._visualization_data.word_dict["data"], sample
        )
    else:
        subset = scatterplot_structure._visualization_data.word_dict["data"]
    df = pd.DataFrame(subset)
    if (
        "etc" in scatterplot_structure._visualization_data.word_dict["data"][0]
        and "ColorScore"
        in scatterplot_structure._visualization_data.word_dict["data"][0]["etc"]
    ):
        df["s"] = [d["etc"]["ColorScore"] for d in subset]
    info = scatterplot_structure._visualization_data.word_dict["info"]
    n_docs = len(scatterplot_structure._visualization_data.word_dict["docs"]["texts"])
    n_words = df.shape[0]

    if scatterplot_structure._show_characteristic:
        characteristic_terms = list(
            df.sort_values("bg", axis=0, ascending=False).iloc[:23].term
        )

    if df.s.isna().sum() > 0:
        colors = "k"
    else:
        colors = df.s

    # Initiate plotting
    ax_plot = None
    if scatterplot_structure._ignore_categories:
        if scatterplot_structure._show_characteristic:
            fig, axs = plt.subplots(1, 2, figsize=figsize, width_ratios=[5, 1], dpi=dpi)
            ax_char = axs[1]
        else:
            fig, ax_plot = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
    else:
        if scatterplot_structure._show_characteristic:
            fig, axs = plt.subplots(
                1, 3, figsize=figsize, width_ratios=[6, 1, 1], dpi=dpi
            )
            ax_cat = axs[1]
            ax_char = axs[2]
        else:
            fig, axs = plt.subplots(1, 2, figsize=figsize, width_ratios=[5, 1], dpi=dpi)
            ax_cat = axs[1]
    plt.tight_layout()
    if ax_plot is None:
        ax_plot = axs[0]
    ax_plot.scatter(df.x, df.y, c=colors, s=scatter_size, cmap=cmap)
    xlims = ax_plot.get_xlim()
    ylims = ax_plot.get_ylim()

    ta.allocate_text(
        fig,
        ax_plot,
        df.x,
        df.y,
        df.term,
        xlims,
        ylims,
        x_scatter=df.x,
        y_scatter=df.y,
        textsize=textsize,
        distance_margin_fraction=distance_margin_fraction,
        draw_lines=draw_lines,
        linecolor=linecolor,
        draw_all=draw_all,
        nbr_candidates=nbr_candidates,
    )

    # Design settings
    ax_plot.spines.right.set_visible(False)
    ax_plot.spines.top.set_visible(False)
    if xlabel is not None:
        ax_plot.set_xlabel(xlabel)
    elif scatterplot_structure._x_label is not None:
        ax_plot.set_xlabel(scatterplot_structure._x_label)
    elif not scatterplot_structure._ignore_categories:
        ax_plot.set_xlabel(info["not_category_name"])
    else:
        pass
    if ylabel is not None:
        ax_plot.set_ylabel(ylabel)
    elif scatterplot_structure._y_label is not None:
        ax_plot.set_ylabel(scatterplot_structure._y_label)
    elif not scatterplot_structure._ignore_categories:
        ax_plot.set_ylabel(info["category_name"])
    else:
        pass
    ax_plot.locator_params(axis="y", nbins=3)
    ax_plot.locator_params(axis="x", nbins=3)
    try:
        if scatterplot_structure._x_axis_labels is not None:
            ax_plot.set_xticks(
                ax_plot.get_xticks()[1:-1], scatterplot_structure._x_axis_labels, size=7
            )
        else:
            ax_plot.set_xticks(
                ax_plot.get_xticks()[1:-1], ["Low", "Medium", "High"], size=7
            )
    except:
        pass
    try:
        if scatterplot_structure._y_axis_labels is not None:
            ax_plot.set_yticks(
                ax_plot.get_yticks()[1:-1],
                scatterplot_structure._y_axis_labels,
                size=7,
                rotation=90,
            )
        else:
            ax_plot.set_yticks(
                ax_plot.get_yticks()[1:-1],
                ["Low", "Medium", "High"],
                size=7,
                rotation=90,
            )
    except:
        pass
    if scatterplot_structure._show_diagonal:
        ax_plot.plot(
            [xlims[0], xlims[1]],
            [ylims[0], ylims[1]],
            color="k",
            linestyle="dashed",
            linewidth=1,
            alpha=0.3,
        )

    # Categories
    alignment = {"horizontalalignment": "left", "verticalalignment": "top"}
    if not scatterplot_structure._ignore_categories:
        yp = [i / 22 for i in range(22)]
        yp.reverse()
        ax_cat.text(
            0.0,
            yp[0],
            "Top " + info["category_name"],
            weight="bold",
            size="medium",
            **alignment,
        )
        for i, term in enumerate(info["category_terms"]):
            ax_cat.text(0.0, yp[i + 1], term, size="small", **alignment)
        ax_cat.text(
            0.0,
            yp[11],
            "Top " + info["not_category_name"],
            weight="bold",
            size="medium",
            **alignment,
        )
        for i, term in enumerate(info["not_category_terms"]):
            axs[1].text(0.0, yp[i + 12], term, size="small", **alignment)
        ax_cat.spines.right.set_visible(False)
        ax_cat.spines.top.set_visible(False)
        ax_cat.spines.bottom.set_visible(False)
        ax_cat.spines.left.set_visible(False)
        ax_cat.set_xticks([])
        ax_cat.set_yticks([])

    # Characteristics
    if scatterplot_structure._show_characteristic:
        yp = [i / 24 for i in range(24)]
        yp.reverse()
        ax_char.text(
            0.0, yp[0], "Characteristic", weight="bold", size="medium", **alignment
        )
        for i, term in enumerate(characteristic_terms):
            ax_char.text(0.0, yp[i + 1], term, size="small", **alignment)
        ax_char.spines.right.set_visible(False)
        ax_char.spines.top.set_visible(False)
        ax_char.spines.bottom.set_visible(False)
        ax_char.spines.left.set_visible(False)
        ax_char.set_xticks([])
        ax_char.set_yticks([])

    fig.suptitle(f"Document count: {n_docs} - Word count: {n_words}", ha="right")
    return fig