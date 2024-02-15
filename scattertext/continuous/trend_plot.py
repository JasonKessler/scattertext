import dataclasses
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable
from sklearn.neighbors import KNeighborsRegressor

import numpy as np
import pandas as pd

from scattertext.dispersion.dispersion import Dispersion
from scattertext.indexstore import IndexStoreFromList
from scattertext.continuous.correlations import Correlations
from scattertext.termranking import AbsoluteFrequencyRanker
from scattertext.termranking.TermRanker import TermRanker
from scattertext.TermDocMatrix import TermDocMatrix
from scattertext.Scalers import get_scaler_name, scale_center_zero_abs, scale, dense_rank
from scattertext.smoothing.mean_isotonic import MeanIsotonic


@dataclasses.dataclass
class TrendPlotPresets:
    x_label: str
    y_label: str
    y_axis_labels: List[str]
    x_axis_labels: List[str]
    tooltip_columns: List[str]
    tooltip_column_names: Dict[str, str]
    header_names: Dict[str, str]
    left_list_column: str


@dataclasses.dataclass
class ScaledAxis:
    orig: np.array
    scaled: np.array


class TrendPlotSettings(ABC):
    def __init__(self, category_order: Optional[List] = None, **kwargs):
        self.category_order = category_order

    def get_category_ranks(self, corpus: TermDocMatrix) -> np.array:
        if self.category_order is None:
            self.category_order = list(sorted(corpus.get_categories()))
        category_rank = {cat: i for i, cat in enumerate(self.category_order)}
        return np.array([category_rank[category] for category in corpus.get_category_names_by_row()])

    @abstractmethod
    def get_plot_params(self) -> TrendPlotPresets:
        pass


class DispersionPlotSettings(TrendPlotSettings):
    def __init__(
            self,
            category_order: List = None,
            metric: str = 'DA',
            use_residual: bool = True,
            term_ranker: Optional[TermRanker] = None,
            frequency_scaler: Optional[Callable[[np.array], np.array]] = None,
            dispersion_scaler: Optional[Callable[[np.array], np.array]] = None,
            regressor: Optional = None,
    ):
        TrendPlotSettings.__init__(self, category_order=category_order)
        self.metric = metric
        self.use_residual = use_residual
        self.frequency_scaler = dense_rank if frequency_scaler is None else frequency_scaler
        self.dispersion_scaler = (scale_center_zero_abs if use_residual else scale) \
            if dispersion_scaler is None else dispersion_scaler # log_scale_with_negatives, log_scale
        self.term_ranker = AbsoluteFrequencyRanker if term_ranker is None else term_ranker
        self.regressor = MeanIsotonic() if regressor is None else regressor


    def get_plot_params(self) -> TrendPlotPresets:
        return TrendPlotPresets(
            x_label=' '.join(['Frequency', get_scaler_name(self.frequency_scaler).strip()]),
            y_label=('Frequency-adjusted ' if self.use_residual else '') + self.metric,
            x_axis_labels=['Low', 'Medium', 'High'],
            y_axis_labels=['More Concentrated', 'Medium', 'More Dispersion'],
            tooltip_column_names={'Frequency': 'Frequency', 'Y': 'Residual ' + self.metric},
            tooltip_columns=['Frequency', 'Y'],
            header_names={'upper': 'Dispersed', 'lower': 'Concentrated'},
            left_list_column='Y'
        )

    def get_x_axis(self, corpus: TermDocMatrix, non_text: bool = False) -> ScaledAxis:
        rank_df = self.term_ranker(corpus).set_non_text(non_text=non_text).get_ranks('')
        frequencies = rank_df.sum(axis=1)
        return ScaledAxis(orig=frequencies, scaled=self.frequency_scaler(frequencies))


class CorrelationPlotSettings(TrendPlotSettings):
    def __init__(
            self,
            category_order: List = None,
            correlation_type: str = 'spearmanr',
            term_ranker: Optional[TermRanker] = None,
            frequency_scaler: Optional[Callable[[np.array], np.array]] = None
    ):
        TrendPlotSettings.__init__(self, category_order=category_order)
        self.correlation_type = correlation_type
        self.term_ranker = AbsoluteFrequencyRanker if term_ranker is None else term_ranker
        self.frequency_scaler = dense_rank if frequency_scaler is None else frequency_scaler

    def get_plot_params(self) -> TrendPlotPresets:
        return TrendPlotPresets(
            x_label=' '.join(['Frequency', get_scaler_name(self.frequency_scaler).strip()]),
            y_label=self.correlation_type.title(),
            x_axis_labels=['Low', 'Medium', 'High'],
            y_axis_labels=['Anti-correlated', 'No-correlation', 'Correlated'],
            tooltip_column_names={'Frequency': 'Frequency',
                                  'Y': Correlations.get_notation_name(self.correlation_type)},
            tooltip_columns=['Frequency', 'Y'],
            header_names={'upper': 'Most correlated', 'lower': 'Most anti-correlated'},
            left_list_column='Y'
        )

    def get_x_axis(self, corpus: TermDocMatrix, non_text: bool = False) -> ScaledAxis:
        rank_df = self.term_ranker(corpus).set_non_text(non_text=non_text).get_ranks('')
        frequencies = rank_df.sum(axis=1)
        return ScaledAxis(orig=frequencies, scaled=self.frequency_scaler(frequencies))


class TimePlotSettings(TrendPlotSettings):
    def __init__(
            self,
            category_order: List = None,
            dispersion_metric: str = 'DA',
            use_residual: bool = False,
            dispersion_scaler: Optional[Callable[[np.array], np.array]] = None,
            term_ranker: Optional[TermRanker] = None,
            regressor: Optional = None,
    ):
        TrendPlotSettings.__init__(self, category_order=category_order)
        self.y_axis_metric = dispersion_metric
        self.dispersion_scaler = dispersion_scaler
        self.use_residual = use_residual
        self.term_ranker = AbsoluteFrequencyRanker if term_ranker is None else term_ranker
        self.regressor = KNeighborsRegressor(weights='distance') if regressor is None else regressor

    def get_plot_params(self) -> TrendPlotPresets:
        return TrendPlotPresets(
            x_label='Mean Category Position',
            y_label=' '.join([get_scaler_name(self.dispersion_scaler),
                              ('Residual ' if self.use_residual else '') + self.y_axis_metric]).strip(),
            y_axis_labels=['High ' + self.y_axis_metric, '', 'Low ' + self.y_axis_metric],
            x_axis_labels=[self.category_order[0],
                           self.category_order[round(len(self.category_order)/2)],
                           self.category_order[-1]],
            tooltip_column_names={
                'Frequency': 'Frequency',
                'MeanCategory': 'Mean'
            },
            tooltip_columns=['Frequency', 'MeanCategory'],
            header_names={'upper': 'Most Dispersed', 'lower': 'Most Concentrated'},
            left_list_column='Y'
        )


class TimePlotPositioner:
    def __init__(self,
                 corpus: TermDocMatrix,
                 category_order: List,
                 non_text: bool = True,
                 dispersion_metric: str = 'DA',
                 use_residual: bool = False):
        self.corpus = corpus
        self.category_order = category_order
        assert set(category_order) == set(corpus.get_categories())
        self.non_text = non_text
        self.dispersion_metric = dispersion_metric
        self.use_residual = use_residual



    def get_position_df(self) -> pd.DataFrame:
        category_order_idx = IndexStoreFromList.build(self.category_order)
        category_values = np.array([category_order_idx.getidx(v)
                                    for v in self.corpus.get_category_names_by_row()])

        tdm = self.corpus.get_term_doc_mat(non_text=self.non_text)
        freq = tdm.sum(axis=0).A1

        dispersion = Dispersion(
            corpus=self.corpus,
            non_text=self.non_text,
            use_categories_as_documents=True,
        )
        if self.use_residual:
            dispersion_df = dispersion.get_adjusted_metric_df(metric=self.dispersion_metric)
            dispersion_value = dispersion_df['Residual'].values
        else:
            dispersion_df = dispersion.get_df(include_da=self.dispersion_metric == 'DA')
            dispersion_value = dispersion_df[self.dispersion_metric].values

        position_df = pd.DataFrame({
            'Frequency': freq,
            'Mean': (category_values * tdm) / freq,
            'term': self.corpus.get_terms(use_metadata=self.non_text),
            'Dispersion': dispersion_value
        }).set_index('term').assign(
            MeanCategory=lambda df: np.array(self.category_order)[df.Mean.round().astype(int)]
        )

        return position_df
