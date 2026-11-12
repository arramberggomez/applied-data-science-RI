"""Command-line entry point: ``uv run python -m applied_data_science_ri <step>``.

Examples:
    python -m applied_data_science_ri download
    python -m applied_data_science_ri clean --nrows 100000   # quick run on a sample
    python -m applied_data_science_ri all
"""

import argparse

from . import config, pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="applied_data_science_ri",
        description="US Air Quality: multi-station aggregation and pollution forecasting",
    )
    sub = parser.add_subparsers(dest="step", required=True)

    p = sub.add_parser("download", help="download the raw dataset from Kaggle")
    p.add_argument("--force", action="store_true", help="re-download even if present")

    p = sub.add_parser("clean", help="audit and clean the raw data")
    p.add_argument("--nrows", type=int, default=None, help="only read the first N rows")

    sub.add_parser("eda", help="generate exploratory figures")
    sub.add_parser("features", help="build the model-ready feature matrix")
    sub.add_parser("train", help="tune and fit all models")

    p = sub.add_parser("evaluate", help="evaluate fitted models")
    p.add_argument("--split", choices=["valid", "test"], default="valid")

    p = sub.add_parser("all", help="run the full pipeline end to end")
    p.add_argument("--nrows", type=int, default=None, help="only read the first N rows")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config.ensure_dirs()
    match args.step:
        case "download":
            pipeline.run_download(force=args.force)
        case "clean":
            pipeline.run_clean(nrows=args.nrows)
        case "eda":
            pipeline.run_eda()
        case "features":
            pipeline.run_features()
        case "train":
            pipeline.run_train()
        case "evaluate":
            pipeline.run_evaluate(split=args.split)
        case "all":
            pipeline.run_all(nrows=args.nrows)


if __name__ == "__main__":
    main()
