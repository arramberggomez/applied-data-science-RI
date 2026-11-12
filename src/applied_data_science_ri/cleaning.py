"""Cleaning: turn the raw file into one row per station and day.

Decisions (based on notebooks/01_data_exploration.ipynb):
  * units: each pollutant uses a single unit, so the unit columns are dropped
  * "Country Of Mexico" is not a US state, so its rows are dropped
  * duplicates: each station-day appears on several rows because SO2 and CO are
    measured with several methods. We collapse them into one row: average the
    means and AQIs (the mean skips missing AQIs), keep the highest max value
  * negative concentrations (small, sensor noise around zero) are set to 0
  * every station gets one row per calendar day between its first and last
    measurement; days without data stay as NaN
"""

import pandas as pd

from . import config
from .utils import log

STATION_INFO = ["state_code", "county_code", "site_num", "state", "county", "city"]


def audit(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: type, % missing, number of unique values, min and max."""
    numeric = df.select_dtypes("number")
    return pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "pct_missing": df.isna().mean().mul(100).round(1),
            "n_unique": df.nunique(),
            "min": numeric.min(),
            "max": numeric.max(),
        }
    )


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Snake_case names ("NO2 Mean" -> "no2_mean"), "Date Local" -> "date",
    and drop the columns we don't need (address and units)."""
    df = df.rename(columns={"Date Local": config.DATE_COL})
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    unit_cols = [col for col in df.columns if col.endswith("_units")]
    return df.drop(columns=["address", *unit_cols])


def drop_non_us(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the rows from Mexico."""
    return df[df["state"] != "Country Of Mexico"]


def add_station_id(df: pd.DataFrame) -> pd.DataFrame:
    """One ID per station, e.g. "6-37-1103" (state code - county code - site number)."""
    station_id = (
        df["state_code"].astype(str)
        + "-"
        + df["county_code"].astype(str)
        + "-"
        + df["site_num"].astype(str)
    )
    return df.assign(**{config.STATION_ID: station_id})


def deduplicate_station_days(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse the duplicated rows into one row per station and day."""
    rules = {}
    for col in df.columns:
        if col.endswith(("_mean", "_aqi")):
            rules[col] = "mean"
        elif col.endswith("_max_value"):
            rules[col] = "max"
        elif col not in (config.STATION_ID, config.DATE_COL):
            rules[col] = "first"  # station info and max hour
    return df.groupby([config.STATION_ID, config.DATE_COL], as_index=False).agg(rules)


def fix_negatives(df: pd.DataFrame) -> pd.DataFrame:
    """Set negative concentrations to 0."""
    value_cols = [col for col in df.columns if col.endswith(("_mean", "_max_value"))]
    df[value_cols] = df[value_cols].clip(lower=0)
    return df


def reindex_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Give every station one row per day, so that "7 days ago" is always 7 rows back.
    Days with no measurement get NaN values."""
    stations = []
    for station, group in df.groupby(config.STATION_ID):
        days = pd.date_range(group[config.DATE_COL].min(), group[config.DATE_COL].max())
        group = group.set_index(config.DATE_COL).reindex(days)
        group[config.STATION_ID] = station
        group[STATION_INFO] = group[STATION_INFO].ffill()  # same for every day of a station
        stations.append(group)
    df = pd.concat(stations).rename_axis(config.DATE_COL).reset_index()
    codes = ["state_code", "county_code", "site_num"]
    df[codes] = df[codes].astype(int)  # the empty days had turned them into floats
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Run every cleaning step in order."""
    n_in = len(df)
    df = (
        df.pipe(standardize_columns)
        .pipe(drop_non_us)
        .pipe(add_station_id)
        .pipe(deduplicate_station_days)
        .pipe(fix_negatives)
        .pipe(reindex_daily)
    )
    log.info("Cleaning: %s rows -> %s rows", f"{n_in:,}", f"{len(df):,}")
    return df
