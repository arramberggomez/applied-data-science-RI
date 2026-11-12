"""Exploratory data analysis. Every function saves one figure to ``report/figures``."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from . import config
from .utils import log

AQI_COLS = [f"{p.lower()}_aqi" for p in config.POLLUTANTS]
TARGET_AQI = f"{config.TARGET_POLLUTANT.lower()}_aqi"


def set_style() -> None:
    """Same look for every figure."""
    sns.set_theme(context="paper", style="whitegrid", palette="colorblind")
    plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "savefig.bbox": "tight"})


def save_fig(fig: plt.Figure, name: str) -> Path:
    """Save ``fig`` as ``report/figures/<name>.png`` and close it."""
    path = config.FIGURES_DIR / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    log.info("Saved figure %s", path.name)
    return path


def plot_station_coverage(df: pd.DataFrame) -> Path:
    """Number of stations reporting each month: shows gaps and stations coming and going."""
    reporting = df.dropna(subset=[TARGET_AQI])
    per_month = reporting.groupby(reporting[config.DATE_COL].dt.to_period("M"))[
        config.STATION_ID
    ].nunique()

    fig, ax = plt.subplots(figsize=(8, 3))
    per_month.plot(ax=ax)
    ax.set(title="Stations reporting per month", xlabel="", ylabel="Stations")
    return save_fig(fig, "station_coverage")


def plot_distributions(df: pd.DataFrame) -> Path:
    """Histogram of the AQI of each pollutant."""
    fig, axes = plt.subplots(1, len(AQI_COLS), figsize=(12, 3))
    for ax, col in zip(axes, AQI_COLS, strict=True):
        sns.histplot(df[col].dropna(), bins=50, ax=ax)
        ax.set(title=col.split("_")[0].upper(), xlabel="AQI", ylabel="")
    fig.suptitle("Daily AQI distribution per pollutant", y=1.05)
    return save_fig(fig, "aqi_distributions")


def plot_long_term_trends(df: pd.DataFrame) -> Path:
    """Yearly national mean AQI of each pollutant (2016 is only Jan-May, so it is left out)."""
    yearly = df[df[config.DATE_COL].dt.year < 2016]
    yearly = yearly.groupby(yearly[config.DATE_COL].dt.year)[AQI_COLS].mean()

    fig, ax = plt.subplots(figsize=(8, 4))
    yearly.plot(ax=ax, marker="o")
    ax.set(title="Yearly mean AQI", xlabel="", ylabel="Mean AQI")
    ax.legend([c.split("_")[0].upper() for c in AQI_COLS])
    return save_fig(fig, "long_term_trends")


def plot_seasonality(df: pd.DataFrame) -> Path:
    """Mean AQI by month and by day of the week."""
    dates = df[config.DATE_COL]
    by_month = df.groupby(dates.dt.month)[AQI_COLS].mean()
    by_weekday = df.groupby(dates.dt.dayofweek)[AQI_COLS].mean()
    labels = [c.split("_")[0].upper() for c in AQI_COLS]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    by_month.plot(ax=ax1, marker="o", legend=False)
    ax1.set(title="By month", xlabel="Month", ylabel="Mean AQI", xticks=range(1, 13))
    by_weekday.plot(ax=ax2, marker="o", legend=False)
    ax2.set(title="By day of the week", xlabel="", ylabel="")
    ax2.set_xticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    fig.legend(labels, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.05))
    return save_fig(fig, "seasonality")


def plot_correlations(df: pd.DataFrame) -> Path:
    """Left: correlation between pollutants. Right: how much today's target AQI
    is correlated with its value k days before (autocorrelation)."""
    lags = range(1, 31)
    autocorr = [
        df[TARGET_AQI].corr(df.groupby(config.STATION_ID)[TARGET_AQI].shift(k)) for k in lags
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    sns.heatmap(df[AQI_COLS].corr(), annot=True, fmt=".2f", cmap="vlag", center=0, ax=ax1)
    ax1.set_title("Correlation between pollutants (AQI)")
    ax2.bar(lags, autocorr)
    ax2.set(
        title=f"{config.TARGET_POLLUTANT} AQI: correlation with k days before",
        xlabel="k (days)",
        ylabel="Correlation",
    )
    return save_fig(fig, "correlations")


def plot_by_state(df: pd.DataFrame) -> Path:
    """Mean target AQI per state."""
    by_state = df.groupby("state", observed=True)[TARGET_AQI].mean().sort_values()

    fig, ax = plt.subplots(figsize=(6, 9))
    by_state.plot.barh(ax=ax)
    ax.set(title=f"Mean {config.TARGET_POLLUTANT} AQI per state", xlabel="Mean AQI", ylabel="")
    return save_fig(fig, "aqi_by_state")


def run_eda(df: pd.DataFrame) -> list[Path]:
    """Make every EDA figure from the cleaned table."""
    set_style()
    steps = [
        plot_station_coverage,
        plot_distributions,
        plot_long_term_trends,
        plot_seasonality,
        plot_correlations,
        plot_by_state,
    ]
    return [step(df) for step in steps]
