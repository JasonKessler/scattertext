from _bisect import bisect_left

import numpy as np
import pandas as pd


def scale_font_size(scores: np.array, min_size=9, max_size=20) -> np.array:
    bin_boundaries = np.histogram_bin_edges(
        np.log(scores), bins=max_size - min_size
    )
    return pd.Series(scores).apply(np.log).apply(
        lambda x: bisect_left(bin_boundaries, x) + min_size).values


def get_ternary_colors(scores: np.array,
                       negative_color="#d72d00",
                       zero_color="#bdbdbd",
                       positive_color="#2a3e63") -> np.array:
    colors = np.array([zero_color] * len(scores))
    colors[scores < 0] = negative_color
    colors[scores > 0] = positive_color
    return list(colors)
