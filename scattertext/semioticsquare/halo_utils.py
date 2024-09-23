import pandas as pd
import numpy as np

from scattertext.Scalers import stretch_neg1_to_1

FINE_PART_TO_SELECTION = {
    0: 'bottom',
    1: 'bottom_left',
    2: 'bottom_left',
    3: 'left',
    4: 'left',
    5: 'top_left',
    6: 'top_left',
    7: 'top',
    8: 'top',
    9: 'top_right',
    10: 'top_right',
    11: 'right',
    12: 'right',
    13: 'bottom_right',
    14: 'bottom_right',
    15: 'bottom'
}


def term_coordinates_to_halo(term_coordinates_df: pd.DataFrame, num_terms: int = 5) -> dict:
    return dict(
        add_radial_parts_and_mag_to_term_coordinates(
            term_coordinates_df=term_coordinates_df
        ).sort_values(by='Mag', ascending=False).groupby('Part').apply(
            lambda gdf: list(gdf.iloc[:num_terms].index)
        )
    )


def add_radial_parts_and_mag_to_term_coordinates(term_coordinates_df: pd.DataFrame) -> pd.DataFrame:
    assert 'x' in term_coordinates_df.columns
    assert 'y' in term_coordinates_df.columns

    radial_term_coordinates_df = term_coordinates_df.apply(stretch_neg1_to_1).assign(
        FinePart=(lambda df: (((np.arctan2(df.x, df.y) + np.pi) * 360 / (2 * np.pi)) // (45 / 2)).astype(int)),
        Part=lambda df: df.FinePart.apply(FINE_PART_TO_SELECTION.get),
        Mag=lambda df: df.x ** 2 + df.y ** 2,
    )
    return radial_term_coordinates_df
