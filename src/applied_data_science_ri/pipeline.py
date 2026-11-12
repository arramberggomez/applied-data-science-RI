"""Glue code that chains the pipeline stages.

Each stage reads the artefact of the previous one from disk and writes its own, so
stages can be re-run independently (e.g. iterate on models without re-cleaning).

    download -> data/raw/*.csv
    clean    -> data/processed/pollution_clean.parquet
    features -> data/processed/features.parquet
    eda      -> report/figures/*.png
    train    -> models/*.joblib
    evaluate -> report/tables/metrics_<split>.csv
"""

from . import cleaning, config, data, eda, evaluation, features, models
from .utils import log, memory_usage_mb, timer


def run_download(force: bool = False) -> None:
    data.download_raw_data(force=force)


def run_clean(nrows: int | None = None) -> None:
    with timer("load raw"):
        raw = data.load_raw(nrows=nrows)
    log.info("Raw data: %s rows, %.0f MB", f"{len(raw):,}", memory_usage_mb(raw))
    cleaning.audit(raw).to_csv(config.TABLES_DIR / "raw_audit.csv")
    with timer("clean"):
        clean = cleaning.clean(raw)
    data.save_parquet(clean, config.CLEAN_FILE)


def run_eda() -> None:
    eda.run_eda(data.load_parquet(config.CLEAN_FILE))


def run_features() -> None:
    clean = data.load_parquet(config.CLEAN_FILE)
    with timer("features"):
        feats = features.build_features(clean)
    data.save_parquet(feats, config.FEATURES_FILE)


def run_train() -> None:
    feats = data.load_parquet(config.FEATURES_FILE)
    train, _valid, _test = models.temporal_split(feats)
    X_train, y_train = features.split_xy(train)
    with timer("training"):
        models.train_all(X_train, y_train)


def run_evaluate(split: str = "valid") -> None:
    """Evaluate the saved models on ``valid`` (model selection) or ``test`` (final, once)."""
    feats = data.load_parquet(config.FEATURES_FILE)
    _train, valid, test = models.temporal_split(feats)
    X, y = features.split_xy(valid if split == "valid" else test)
    fitted = {name: models.load_model(name) for name in models.get_models()}

    table = evaluation.evaluate_models(fitted, X, y)
    table.to_csv(config.TABLES_DIR / f"metrics_{split}.csv", index=False)
    log.info("\n%s", table.to_string(index=False))


def run_all(nrows: int | None = None) -> None:
    config.ensure_dirs()
    run_download()
    run_clean(nrows=nrows)
    run_eda()
    run_features()
    run_train()
    run_evaluate("valid")
