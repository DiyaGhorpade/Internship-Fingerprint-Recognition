# services/data_loader.py

import pandas as pd
from pathlib import Path
from functools import lru_cache

DATA_PATH = Path("blood_fingerprint_FULL.csv")  # adjust if needed

@lru_cache(maxsize=1)
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"❌ Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    # Normalize column names for safety
    df.columns = [c.strip().lower() for c in df.columns]

    # Ensure required columns exist
    required_cols = {"blood_type", "fingerprint_type"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"❌ Required columns missing. Found: {df.columns} "
            f"Needed: {required_cols}"
        )

    return df
