"""Models: baselines, machine-learning models, time-aware split and training.

TODO (modelling team):
  * at least one simple baseline to beat (e.g. "tomorrow = today")
  * a few models, justified theoretically in the report (section 4)
  * split by date, never shuffled (see TRAIN_END / VALID_END in config.py)
  * hyperparameter tuning with a time-aware cross-validation
"""

import joblib
import pandas as pd
from sklearn.base import BaseEstimator

from . import config


def get_models() -> dict[str, BaseEstimator]:
    """Every model to compare, by name."""
    raise NotImplementedError


def temporal_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split the feature table by date into train / validation / test."""
    raise NotImplementedError


def train_all(X: pd.DataFrame, y: pd.Series) -> dict[str, BaseEstimator]:
    """Tune and fit every model from :func:`get_models` and save each with :func:`save_model`."""
    raise NotImplementedError


def save_model(model: BaseEstimator, name: str) -> None:
    path = config.MODELS_DIR / f"{name}.joblib"
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(name: str) -> BaseEstimator:
    return joblib.load(config.MODELS_DIR / f"{name}.joblib")
