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

# Define category mapping rules based on keywords
subcategory_map = {
    "Groceries": ["supermarket", "walmart", "trader joe", "kroger", "costco", "whole foods"],
    "Dining": ["restaurant", "starbucks", "mcdonalds", "cafe", "chipotle", "dunkin", "burger king", "subway"],
    "Utilities": ["electric", "water", "internet", "gas & electric", "xfinity", "verizon", "spectrum"],
    "Transport": ["uber", "lyft", "shell", "chevron", "transit", "costco gas"],
    "Shopping": ["amazon", "target", "best buy", "walmart", "home depot", "lowes", "REI", "nike", "adidas", "zara", "h&m", "abercrombie", "gap", "old navy", "macys", "nordstrom", "sephora", "ulta"],
    "Subscriptions": ["netflix", "spotify", "hulu", "disney+", "peacock", "adobe", "dropbox", "ZWIFT", "peloton", "apple music", "prime video"],
    "Travel": ["airbnb", "delta", "united", "southwest", "expedia", "hotels.com", "alaska air", "american airlines", "united airlines", "jetblue", "travelocity", "kayak"],
}

category_map = {
    "Essentials": ["Groceries", "Utilities", "Transport"],
    "Non-Essentials": ["Dining", "Shopping", "Subscriptions", "Travel"],
    "Investments": ["Savings", "Investments", "Retirement"],
}

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
    df["txn_id"] = df.apply(lambda r: hashlib.md5(
            f"{r['date']}{r['description']}{r['amount']}{r['source']}".encode()
        ).hexdigest(), axis=1)
    return df


def subcategorize(desc: str) -> str:
    """
    Fill in missing categories using simple keyword rules on `description`
    (e.g. "STARBUCKS" -> "Coffee", "SHELL OIL" -> "Gas").
    TODO: start with a small dict of {keyword: category}, expand over time.
    Leave category as-is if the source already provided one.
    """
    desc_lower = str(desc).lower()
    for category, keywords in subcategory_map.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    return "Other"  # Default category if no keywords match

def categorize(subcategory: str) -> str:
    """
    Fill in missing categories using simple keyword rules on `description`
    (e.g. "STARBUCKS" -> "Coffee", "SHELL OIL" -> "Gas").
    TODO: start with a small dict of {keyword: category}, expand over time.
    Leave category as-is if the source already provided one.
    """
    sub_cat_lower = str(subcategory).lower()
    for category, keywords in category_map.items():
        for keyword in keywords:
            if keyword in sub_cat_lower:
                return category
    return "Other"  # Default category if no keywords match


def normalize_statement(stmt: RawStatement, source_cfg: dict) -> pd.DataFrame:
    """Run one RawStatement through the full normalization pipeline."""
    df = stmt.df.copy()
    df = rename_columns(df, source_cfg["column_map"])
    df = normalize_dates(df, source_cfg["date_format"])
    df = normalize_amount_sign(df, source_cfg["amount_sign"])
    df["source"] = stmt.source_name
    df["month"] = df["date"].dt.to_period("M")  # Add month column for grouping
    df = add_txn_id(df)
    df["subcategory"] = df["description"].apply(subcategorize)
    df["category"] = df["subcategory"].apply(categorize)
    df = df.dropna(subset=['amount']) # Drop rows where amount is NaN 
    return df[NORMALIZED_COLUMNS]


def transform_all(raw_statements: list, config: dict) -> pd.DataFrame:
    """
    Normalize every RawStatement, concatenate into one master DataFrame,
    and dedupe on txn_id.
    """
    normalized_frames = []

    for stmt in raw_statements:
        source_cfg = config["sources"][stmt.source_name]
        normalized_frames.append(normalize_statement(stmt, source_cfg))
    
    combined = pd.concat(normalized_frames, ignore_index=True)
    combined = combined.drop_duplicates(subset="txn_id")
    combined = combined.sort_values("date")

    return combined


if __name__ == "__main__":
    from extract import load_config, extract_all

    cfg = load_config()
    raw = extract_all(cfg)
    clean = transform_all(raw, cfg)
    
    # Force pandas to print all columns and format nicely
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'center')

    print(clean.head(10))  # Pint first 10 rows without index
    print(f"Total transactions after deduplication: {len(clean)}")