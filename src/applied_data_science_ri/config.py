"""Central configuration: paths, dataset constants and experiment settings.

Every other module imports from here, so changing an experiment (target pollutant,
forecast horizon, split dates...) only requires editing this file.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # untouched download from Kaggle
PROCESSED_DIR = DATA_DIR / "processed"  # cleaned data and feature matrix

MODELS_DIR = PROJECT_ROOT / "models"  # fitted estimators (.joblib)
REPORT_DIR = PROJECT_ROOT / "report"  # LaTeX report + generated figures/tables
FIGURES_DIR = REPORT_DIR / "figures"
TABLES_DIR = REPORT_DIR / "tables"

# File names of the artefacts produced by each pipeline stage
CLEAN_FILE = PROCESSED_DIR / "pollution_clean.parquet"
FEATURES_FILE = PROCESSED_DIR / "features.parquet"

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
# TODO: confirm the slug matches the link in Project_Description.pdf
KAGGLE_DATASET = "sogun3/uspollution"
RAW_FILENAME = "pollution_us_2000_2016.csv"

POLLUTANTS: tuple[str, ...] = ("NO2", "O3", "SO2", "CO")

# Columns that identify a monitoring station after cleaning (snake_case)
STATION_KEYS: list[str] = ["state_code", "county_code", "site_num"]
STATION_ID = "station_id"
DATE_COL = "date"

# ---------------------------------------------------------------------------
# Forecasting task
# ---------------------------------------------------------------------------
TARGET_POLLUTANT = "O3"  # pollutant whose AQI we forecast
HORIZON_DAYS = 1  # forecast t + HORIZON_DAYS from information up to t
TARGET_COL = f"target_{TARGET_POLLUTANT.lower()}_aqi_t{HORIZON_DAYS}"

# Feature engineering
LAGS: tuple[int, ...] = (1, 2, 3, 7, 14, 28)
ROLLING_WINDOWS: tuple[int, ...] = (3, 7, 30)

# Chronological split (inclusive end dates). Never shuffle time series.
TRAIN_END = "2013-12-31"
VALID_END = "2014-12-31"  # test = everything after VALID_END
N_CV_SPLITS = 5  # folds for TimeSeriesSplit during tuning

RANDOM_STATE = 42


def ensure_dirs() -> None:
    """Create every output directory used by the pipeline (idempotent)."""
    for d in (RAW_DIR, PROCESSED_DIR, MODELS_DIR, FIGURES_DIR, TABLES_DIR):
        d.mkdir(parents=True, exist_ok=True)
