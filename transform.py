# ASEO NOTE: claude generated skeleton

"""
transform.py
------------
Takes raw, source-specific DataFrames and normalizes them into ONE
consistent schema:

    txn_id | month | date | category | subcategory | amount | description | source

`amount` convention: negative = money out (expense), positive = money in.
This is the "canonical" sign convention for the whole pipeline — resolve
each source's raw sign convention against this in normalize_amount_sign().
"""

from datetime import datetime
import hashlib

import pandas as pd
import numpy as np

from extract import RawStatement

NORMALIZED_COLUMNS = ["txn_id", "month", "date", "category", "subcategory", "amount", "description", "source"]


def rename_columns(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """
    Rename raw columns to normalized names using column_map from config.
    TODO: invert column_map (normalized -> raw) into (raw -> normalized)
          and call df.rename(columns=...). Handle missing/null mappings
          (e.g. category: null) by creating an empty column instead.
    """
    df = df.copy()
    for normalized_name, raw_name in column_map.items():
        if raw_name is None:
            df[normalized_name] = np.nan  # Create an empty column if mapping is None
        else:
            df = df.rename(columns={raw_name: normalized_name})
    return df


def normalize_dates(df: pd.DataFrame, date_format: str) -> pd.DataFrame:
    """Parse the date column using the source's date_format into pd.Timestamp."""
    # log/flag any rows that failed to parse (errors="coerce" -> NaT)
    df["date"] = pd.to_datetime(df["date"], format=date_format, errors="coerce")
    return df


def normalize_amount_sign(df: pd.DataFrame, amount_sign: str) -> pd.DataFrame:
    """
    Flip sign if needed so the canonical convention holds:
    negative = expense, positive = income/refund.
    """
    if amount_sign == "positive_is_expense":
        df["amount"] = df["amount"] # ensure all values positive
    return df


def add_txn_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a stable hash ID per transaction (date+description+amount+source)
    so we can dedupe transactions that show up in multiple exports
    (e.g. re-downloading overlapping date ranges).
    """
    # TODO: df["txn_id"] = df.apply(lambda r: hashlib.md5(
    #     f"{r['date']}{r['description']}{r['amount']}{r['source']}".encode()
    # ).hexdigest(), axis=1)
    raise NotImplementedError


def categorize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill in missing categories using simple keyword rules on `description`
    (e.g. "STARBUCKS" -> "Coffee", "SHELL OIL" -> "Gas").
    TODO: start with a small dict of {keyword: category}, expand over time.
    Leave category as-is if the source already provided one.
    """
    raise NotImplementedError


def normalize_statement(stmt: RawStatement, source_cfg: dict) -> pd.DataFrame:
    """Run one RawStatement through the full normalization pipeline."""
    df = stmt.df.copy()
    df = rename_columns(df, source_cfg["column_map"])
    df = normalize_dates(df, source_cfg["date_format"])
    df = normalize_amount_sign(df, source_cfg["amount_sign"])
    df["source"] = stmt.source_name
    df = add_txn_id(df)
    df = categorize(df)
    return df[NORMALIZED_COLUMNS]


def transform_all(raw_statements: list, config: dict) -> pd.DataFrame:
    """
    Normalize every RawStatement, concatenate into one master DataFrame,
    and dedupe on txn_id.
    """
    normalized_frames = []

    # TODO:
    # for stmt in raw_statements:
    #     source_cfg = config["sources"][stmt.source_name]
    #     normalized_frames.append(normalize_statement(stmt, source_cfg))

    # TODO: combined = pd.concat(normalized_frames, ignore_index=True)
    # TODO: combined = combined.drop_duplicates(subset="txn_id")
    # TODO: combined = combined.sort_values("date")

    raise NotImplementedError


if __name__ == "__main__":
    from extract import load_config, extract_all

    cfg = load_config()
    raw = extract_all(cfg)
    clean = transform_all(raw, cfg)
    print(clean.head())