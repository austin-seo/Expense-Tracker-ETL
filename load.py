# ASEO NOTE: claude generated skeleton

"""
load.py
-------
Takes the final clean DataFrame and loads it somewhere useful:
  1. Google Sheets (automated, via gspread + service account)
  2. Local CSV (fallback / manual-paste-friendly / semi-automated mode)

Keeping these as separate functions means you can start with option 2
(zero setup) and graduate to option 1 once you've set up API credentials.
"""

from pathlib import Path

import pandas as pd


def save_to_local_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Semi-automated path: write clean data to a local CSV you can
    manually copy/paste or import into Google Sheets.
    """
    # TODO: Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    # TODO: df.to_csv(output_path, index=False)
    raise NotImplementedError


def get_google_sheet_client(credentials_path: str):
    """
    Authenticate with Google Sheets API using a service account.
    TODO:
      import gspread
      from google.oauth2.service_account import Credentials
      scopes = ["https://www.googleapis.com/auth/spreadsheets"]
      creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
      return gspread.authorize(creds)
    """
    raise NotImplementedError


def push_to_google_sheet(
    df: pd.DataFrame,
    sheet_name: str,
    tab_name: str,
    credentials_path: str,
    mode: str = "append",  # "append" or "overwrite"
) -> None:
    """
    Fully automated path: push clean DataFrame directly into a Google Sheet.

    TODO:
      client = get_google_sheet_client(credentials_path)
      sheet = client.open(sheet_name).worksheet(tab_name)

      if mode == "overwrite":
          sheet.clear()
          sheet.update([df.columns.tolist()] + df.values.tolist())
      elif mode == "append":
          # Consider: read existing txn_ids from sheet first,
          # only append rows not already present (avoid dupes).
          existing_ids = set(sheet.col_values(<txn_id_column_index>))
          new_rows = df[~df["txn_id"].isin(existing_ids)]
          sheet.append_rows(new_rows.values.tolist())
    """
    raise NotImplementedError


def load(df: pd.DataFrame, config: dict, mode: str = "local") -> None:
    """
    Dispatcher: mode="local" writes CSV, mode="sheets" pushes to Google Sheets.
    Start with "local" while you're building/debugging, switch to "sheets"
    once the pipeline is trustworthy.
    """
    settings = config["settings"]

    if mode == "local":
        output_path = f"{settings['processed_data_dir']}/clean_transactions.csv"
        save_to_local_csv(df, output_path)
    elif mode == "sheets":
        push_to_google_sheet(
            df,
            sheet_name=settings["google_sheet_name"],
            tab_name=settings["google_sheet_tab"],
            credentials_path=settings["google_credentials_path"],
        )
    else:
        raise ValueError(f"Unknown load mode: {mode}")