"""Evaluation: metrics and figures to compare the models.

TODO (modelling team):
  * choose metrics that fit the problem and justify them in the report
  * compare every model against the baseline(s)
  * figures for the report are saved with ``eda.save_fig`` into ``report/figures``
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator


def regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    """Metrics for one model's predictions."""
    raise NotImplementedError


def evaluate_models(
    models: dict[str, BaseEstimator], X: pd.DataFrame, y: pd.Series
) -> pd.DataFrame:
    """One row per model with its metrics."""
    raise NotImplementedError
