# ASEO NOTE: claude generated skeleton

"""
extract.py
----------
Responsible for ONE thing: finding raw CSV files and loading them into
memory as raw (un-normalized) DataFrames, tagged with which source they
came from. No cleaning/renaming happens here — that's transform.py's job.
"""

from __future__ import annotations # will allow us to use list[RawStatement] in type hints before RawStatement is defined

from pathlib import Path
from dataclasses import dataclass

import pandas as pd
import yaml
import glob


@dataclass
class RawStatement:
    """Container for one raw CSV plus metadata about where it came from."""
    source_name: str          # e.g. "chase_credit_card" — matches config.yaml key
    file_path: Path
    df: pd.DataFrame


def load_config(config_path: str = "config.yaml") -> dict:
    """Load the source/column-mapping config."""
    # open config_path, yaml.safe_load(), return dict
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config



def find_files_for_source(raw_data_dir: Path, file_pattern: str) -> list[Path]:
    """Glob raw_data_dir for files matching this source's pattern."""
    # TODO: return sorted list of Path objects matching file_pattern
    case_insensitive_pattern = file_pattern.replace(".csv", ".[cC][sS][vV]")
    file_paths = glob.glob(f"{raw_data_dir}/{case_insensitive_pattern}")
    return sorted(Path(f) for f in file_paths)


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

    root_data_dir = "./Data/raw"
    
    for source_name, source_cfg in config["sources"].items():
        files = find_files_for_source(root_data_dir, source_cfg["file_pattern"])
        for f in files:
            df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
            raw_statements.append(RawStatement(source_name, f, df))

    return raw_statements


if __name__ == "__main__":
    # Quick manual test when running this file directly
    cfg = load_config()
    statements = extract_all(cfg)
    print(f"Extracted {len(statements)} raw statement(s).")