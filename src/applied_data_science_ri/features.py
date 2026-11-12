"""Features: turn the cleaned station-day table into a table the models can learn from.

Each row is one station on day t. The features only use information known at the
end of day t; the target is the O3 AQI of the next day (t + 1) at the same station.
All shifts and rolling windows are done per station, so values never mix stations.

Choices come from the EDA:
  * O3 is strongly correlated with its own past -> lags and rolling means
  * strong yearly and weekly cycles           -> calendar features
  * differences between states                -> mean O3 of the other stations of the state
"""

import numpy as np
import pandas as pd

from . import config

AQI_COLS = [f"{p.lower()}_aqi" for p in config.POLLUTANTS]
TARGET_AQI = f"{config.TARGET_POLLUTANT.lower()}_aqi"


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Month, day of the week, weekend flag, and the day of the year as sin/cos so
    that 31 December and 1 January end up close to each other."""
    dates = df[config.DATE_COL]
    day_of_year = 2 * np.pi * dates.dt.dayofyear / 365.25
    return df.assign(
        month=dates.dt.month,
        day_of_week=dates.dt.dayofweek,
        is_weekend=(dates.dt.dayofweek >= 5).astype(int),
        doy_sin=np.sin(day_of_year),
        doy_cos=np.cos(day_of_year),
    )


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """``o3_aqi_lag7`` = O3 AQI 7 days before, at the same station (same for every pollutant)."""
    by_station = df.groupby(config.STATION_ID)
    for col in AQI_COLS:
        for k in config.LAGS:
            df[f"{col}_lag{k}"] = by_station[col].shift(k)
    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """Mean of the target AQI over the last w days (up to and including today)."""
    by_station = df.groupby(config.STATION_ID)[TARGET_AQI]
    for w in config.ROLLING_WINDOWS:
        df[f"{TARGET_AQI}_roll{w}"] = by_station.transform(
            lambda s, w=w: s.rolling(w, min_periods=1).mean()
        )
    return df


def add_spatial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Mean target AQI of the *other* stations in the same state on the same day.
    The station itself is excluded so its own value doesn't leak in."""
    groups = df.groupby(["state", config.DATE_COL], observed=True)[TARGET_AQI]
    total = groups.transform("sum")
    count = groups.transform("count")
    own = df[TARGET_AQI].fillna(0)
    own_count = df[TARGET_AQI].notna().astype(int)
    df[f"{TARGET_AQI}_state_others"] = (total - own) / (count - own_count)  # NaN if alone
    return df


def make_target(df: pd.DataFrame) -> pd.DataFrame:
    """Target = O3 AQI of the next day at the same station."""
    df[config.TARGET_COL] = df.groupby(config.STATION_ID)[TARGET_AQI].shift(-config.HORIZON_DAYS)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run every feature step and keep only the rows that have a target."""
    df = (
        df.pipe(add_calendar_features)
        .pipe(add_lag_features)
        .pipe(add_rolling_features)
        .pipe(add_spatial_features)
        .pipe(make_target)
    )
    return df.dropna(subset=[config.TARGET_COL]).reset_index(drop=True)


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate features (X) and target (y). Identifiers and text columns are left out."""
    not_features = [config.TARGET_COL, "state_code", "county_code", "site_num"]
    X = df.select_dtypes("number").drop(columns=not_features)
    return X, df[config.TARGET_COL]
