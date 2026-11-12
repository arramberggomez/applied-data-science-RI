"""Small cross-cutting helpers: logging, timing and memory diagnostics."""

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager

import pandas as pd


def get_logger(name: str = "adsri") -> logging.Logger:
    """Return a module logger with a single, consistently formatted handler."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", "%H:%M:%S")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger()


@contextmanager
def timer(label: str) -> Iterator[None]:
    """Log how long the wrapped block takes: ``with timer("cleaning"): ...``."""
    start = time.perf_counter()
    yield
    log.info("%s took %.1fs", label, time.perf_counter() - start)


def memory_usage_mb(df: pd.DataFrame) -> float:
    """Deep memory footprint of a DataFrame in megabytes."""
    return df.memory_usage(deep=True).sum() / 1024**2
