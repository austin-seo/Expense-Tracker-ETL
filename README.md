# Expense-Tracker-ETL
ETL Pipeline to import, clean, and export credit card and/or bank statement transactions to a Google Sheet for personal budget tracking.

## File Descriptions
- `config.yaml` - establishes mapping per source
- `extract.py` - ingest CSVs
- `trasform.py` - rename/clean/dedupe/categorize transactions/normalize
- `load.py` - write to destination
- `main.py` - orchestrates pipeline

## Dependencies
- `pandas`
- `pyyaml`
- `gspread`
- `google-auth`
