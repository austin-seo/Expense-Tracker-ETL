# ASEO NOTE: claude generated skeleton

"""
extract.py
----------
Responsible for ONE thing: finding raw CSV files and loading them into
memory as raw (un-normalized) DataFrames, tagged with which source they
came from. No cleaning/renaming happens here — that's transform.py's job.
"""

from pathlib import Path
from dataclasses import dataclass

import pandas as pd
import yaml


@dataclass
class RawStatement:
    """Container for one raw CSV plus metadata about where it came from."""
    source_name: str          # e.g. "chase_credit_card" — matches config.yaml key
    file_path: Path
    df: pd.DataFrame


def load_config(config_path: str = "config.yaml") -> dict:
    """Load the source/column-mapping config."""
    # TODO: open config_path, yaml.safe_load(), return dict
    with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    dict = config["sources"] 
    return dict



def find_files_for_source(raw_data_dir: Path, file_pattern: str) -> list[Path]:
    """Glob raw_data_dir for files matching this source's pattern."""
    # TODO: return sorted list of Path objects matching file_pattern
    raise NotImplementedError


def read_csv_safely(file_path: Path) -> pd.DataFrame:
    """
    Read a single CSV with sane defaults.
    TODO: handle common gotchas —
      - encoding issues (try utf-8, fall back to latin-1)
      - stray BOM characters in headers
      - blank leading/trailing rows some banks include
    """
    raise NotImplementedError


def extract_all(config: dict) -> list[RawStatement]:
    """
    Main entry point for this module.
    Loop through every source in config['sources'], find matching files,
    read each into a DataFrame, and return a list of RawStatement objects.
    """
    raw_statements: list[RawStatement] = []

    # TODO:
    # for source_name, source_cfg in config["sources"].items():
    #     files = find_files_for_source(...)
    #     for f in files:
    #         df = read_csv_safely(f)
    #         raw_statements.append(RawStatement(source_name, f, df))

    return raw_statements


if __name__ == "__main__":
    # Quick manual test when running this file directly
    cfg = load_config()
    statements = extract_all(cfg)
    print(f"Extracted {len(statements)} raw statement(s).")