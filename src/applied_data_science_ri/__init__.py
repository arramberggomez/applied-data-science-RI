"""US Air Quality: multi-station aggregation and pollution forecasting.

Package layout (one module per pipeline stage):

    config      paths, constants and experiment settings
    data        download / load / save the raw and intermediate datasets
    cleaning    data-quality audit, deduplication, missing values, outliers
    features    temporal (lags, rolling windows, calendar) and spatial features + target
    eda         exploratory figures saved to report/figures
    models      baselines, model registry, time-aware splits, tuning, training
    evaluation  metrics, per-group breakdowns, diagnostic plots
    pipeline    glue code that chains the stages and persists their outputs
    utils       logging, timing, memory helpers
"""

__version__ = "0.1.0"
