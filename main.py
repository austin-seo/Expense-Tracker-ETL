# ASEO NOTE: claude generated skeleton

"""
main.py
-------
Orchestrates the full E -> T -> L pipeline. This is the file you actually
run (`python main.py`). Keep it thin — all real logic lives in
extract.py / transform.py / load.py. main.py just wires them together
and handles top-level logging/error reporting.
"""

import argparse
import logging

from extract import load_config, extract_all
from transform import transform_all
from load import load


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def run_pipeline(config_path: str, load_mode: str) -> None:
    log = logging.getLogger(__name__)

    log.info("Loading config from %s", config_path)
    config = load_config(config_path)

    log.info("Extracting raw statements...")
    raw_statements = extract_all(config)
    log.info("Extracted %d raw statement file(s).", len(raw_statements))

    log.info("Transforming/normalizing data...")
    clean_df = transform_all(raw_statements, config)
    log.info("Transformed to %d clean transaction rows.", len(clean_df))

    log.info("Loading data (mode=%s)...", load_mode)
    load(clean_df, config, mode=load_mode)
    log.info("Pipeline complete. ✅")


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(description="Personal expense tracker ETL pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument(
        "--mode",
        default="local",
        choices=["local", "sheets"],
        help="Where to load clean data: 'local' CSV or Google 'sheets'",
    )
    args = parser.parse_args()

    run_pipeline(config_path=args.config, load_mode=args.mode)