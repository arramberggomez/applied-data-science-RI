"""Data access: download the Kaggle dataset, read it efficiently, persist artefacts."""

import shutil
from pathlib import Path

import pandas as pd

from . import config
from .utils import log, memory_usage_mb


def download_raw_data(force: bool = False) -> Path:
    """Download the US Pollution dataset into ``data/raw`` and return the CSV path.

    Uses ``kagglehub``, which needs Kaggle credentials (``~/.kaggle/kaggle.json`` or the
    ``KAGGLE_USERNAME`` / ``KAGGLE_KEY`` env vars, which can live in a git-ignored ``.env``).
    """
    target = config.RAW_DIR / config.RAW_FILENAME
    if target.exists() and not force:
        log.info("Raw data already present at %s", target)
        return target

    import kagglehub  # imported lazily: only this step needs network access

    config.ensure_dirs()
    cache_dir = Path(kagglehub.dataset_download(config.KAGGLE_DATASET))
    matches = list(cache_dir.rglob(config.RAW_FILENAME))
    if not matches:
        raise FileNotFoundError(f"{config.RAW_FILENAME} not found in {cache_dir}")
    shutil.copy2(matches[0], target)
    log.info("Downloaded raw data to %s", target)
    return target


def load_raw(path: Path | None = None, nrows: int | None = None) -> pd.DataFrame:
    """Read the raw CSV with lighter column types to save memory.

    With default types the full file takes ~607 MB. Here:
      - ``Unnamed: 0`` (an old row index) is skipped
      - repeated text (state, city, units...) is stored as ``category``
      - measurements are stored as ``float32`` instead of ``float64``
      - ``Date Local`` is parsed as a date

    Args:
        path: CSV location (defaults to ``data/raw/<RAW_FILENAME>``).
        nrows: read only the first ``nrows`` rows; handy for quick tests.
    """
    path = path or config.RAW_DIR / config.RAW_FILENAME

    text_cols = ["Address", "State", "County", "City"]
    text_cols += [f"{p} Units" for p in config.POLLUTANTS]
    value_cols = [
        f"{p} {measure}"
        for p in config.POLLUTANTS
        for measure in ("Mean", "1st Max Value", "1st Max Hour", "AQI")
    ]
    dtypes = {col: "category" for col in text_cols} | {col: "float32" for col in value_cols}

    df = pd.read_csv(
        path,
        usecols=lambda col: col != "Unnamed: 0",
        dtype=dtypes,
        parse_dates=["Date Local"],
        nrows=nrows,
    )
    log.info("Loaded %s rows, %.0f MB", f"{len(df):,}", memory_usage_mb(df))
    return df


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to parquet, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    log.info("Saved %s rows x %s cols to %s", f"{len(df):,}", df.shape[1], path)


def load_parquet(path: Path) -> pd.DataFrame:
    """Read a parquet artefact produced by an earlier pipeline stage."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run the previous pipeline step first.")
    return pd.read_parquet(path)
