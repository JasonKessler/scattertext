from typing import Optional, Callable, Type
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from scattertext.dispersion.dispersion import get_category_dispersion

from scattertext.ParsedCorpus import ParsedCorpus

from scattertext.termranking.TermRanker import TermRanker

IMPUTE_NULL_CEOF = 0.95

NULL_VALUES = {
    'DP': 1,
    'DA': 0,
}

def dispersion_ranker_factory(
    metric: str = 'DP',
    corpus_to_parts: Optional[Callable[[ParsedCorpus], np.array]] = None,
    impute_null_coef: float = IMPUTE_NULL_CEOF
):

    class DispersionRanker(TermRanker):
        def get_ranks(self, label_append: str=f' {metric}') -> pd.DataFrame:
            compare_dispersion_df = get_category_dispersion(
                self._corpus,
                metric=metric,
                corpus_to_parts = corpus_to_parts,
                non_text=self._use_non_text_features,
            )
            rank_df = pd.DataFrame({
                cat+label_append: compare_dispersion_df[f'{cat}_{metric}']
                for cat_i, cat
                in enumerate(self._corpus.get_categories())
            })
            if metric in NULL_VALUES:
                rank_df = rank_df.fillna(NULL_VALUES[metric])
            else:
                for cat in self._corpus.get_categories():
                    cat_compare_df = compare_dispersion_df[[f'{cat}_Frequency', f'{cat}_{metric}']].dropna()
                    r = pearsonr(x=cat_compare_df.dropna()[f'{cat}_Frequency'],
                                 y=cat_compare_df.dropna()[f'{cat}_{metric}']).statistic
                    if r < 0:
                        fill = compare_dispersion_df[f'{cat}_{metric}'].min()*impute_null_coef
                    else:
                        fill = compare_dispersion_df[f'{cat}_{metric}'].max()/impute_null_coef
                    rank_df[cat+label_append] = rank_df[cat+label_append].fillna(fill)
            return rank_df

    return DispersionRanker