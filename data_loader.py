"""
data_loader.py
--------------
Loads, validates, and cleans the COVID-19 India state-wise dataset.
Performs all data quality checks, type casting, and feature engineering.
"""

import pandas as pd
import numpy as np
import os

REQUIRED_COLUMNS = [
    "Date", "State",
    "Daily_Confirmed", "Daily_Recovered", "Daily_Deaths", "Daily_Active",
    "Total_Confirmed", "Total_Recovered", "Total_Deaths", "Total_Active",
]


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load COVID-19 dataset from CSV, clean it, and return a typed DataFrame.

    Steps performed:
      1. Read CSV with correct dtypes
      2. Parse date column
      3. Validate required columns exist
      4. Handle missing values (forward-fill per state)
      5. Remove negative values (data errors)
      6. Add engineered features
    """
    print(f"\n{'='*55}")
    print("  📂  Loading COVID-19 India Dataset")
    print(f"{'='*55}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at: {filepath}\n"
            "Run  python data/generate_data.py  first."
        )

    df = pd.read_csv(filepath, parse_dates=["Date"])

    # ── 1. Validate schema ─────────────────────────────────────────────────
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    print(f"  ✔  Raw rows loaded    : {len(df):>10,}")

    # ── 2. Handle missing / NaN values ─────────────────────────────────────
    numeric_cols = [c for c in df.columns if c not in ("Date", "State")]
    initial_nulls = df[numeric_cols].isnull().sum().sum()
    if initial_nulls > 0:
        df[numeric_cols] = (
            df.groupby("State")[numeric_cols]
              .transform(lambda x: x.ffill().bfill())
        )
        df[numeric_cols] = df[numeric_cols].fillna(0)
        print(f"  ✔  Null values fixed   : {initial_nulls:>10,}")
    else:
        print(f"  ✔  No null values found")

    # ── 3. Clip negatives ──────────────────────────────────────────────────
    df[numeric_cols] = df[numeric_cols].clip(lower=0)

    # ── 4. Sort ────────────────────────────────────────────────────────────
    df = df.sort_values(["State", "Date"]).reset_index(drop=True)

    # ── 5. Feature engineering ─────────────────────────────────────────────
    df = _add_features(df)

    print(f"  ✔  Clean rows         : {len(df):>10,}")
    print(f"  ✔  States covered     : {df['State'].nunique():>10}")
    print(f"  ✔  Date range         :  {df['Date'].min().date()}  →  {df['Date'].max().date()}")
    print(f"  ✔  Columns            : {list(df.columns)}\n")

    return df


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add computed/derived columns (equivalent to DAX measures)."""

    # Recovery Rate  =  Total_Recovered / Total_Confirmed × 100
    df["Recovery_Rate_Pct"] = (
        df["Total_Recovered"] / df["Total_Confirmed"].replace(0, np.nan) * 100
    ).round(2)

    # Case Fatality Rate  =  Total_Deaths / Total_Confirmed × 100
    df["CFR_Pct"] = (
        df["Total_Deaths"] / df["Total_Confirmed"].replace(0, np.nan) * 100
    ).round(4)

    # 7-day rolling average of daily confirmed (per state)
    df["Confirmed_7DMA"] = (
        df.groupby("State")["Daily_Confirmed"]
          .transform(lambda x: x.rolling(7, min_periods=1).mean().round(0))
    )

    # 7-day rolling average of daily deaths
    df["Deaths_7DMA"] = (
        df.groupby("State")["Daily_Deaths"]
          .transform(lambda x: x.rolling(7, min_periods=1).mean().round(0))
    )

    # Month label for grouping
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # Week number
    df["Week"] = df["Date"].dt.isocalendar().week.astype(int)

    # Year
    df["Year"] = df["Date"].dt.year

    return df


def get_national_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate all states → India-level daily time series."""
    agg = {
        "Daily_Confirmed": "sum",
        "Daily_Recovered": "sum",
        "Daily_Deaths":    "sum",
        "Daily_Active":    "sum",
        "Total_Confirmed": "sum",
        "Total_Recovered": "sum",
        "Total_Deaths":    "sum",
        "Total_Active":    "sum",
    }
    nat = df.groupby("Date").agg(agg).reset_index()
    nat["Confirmed_7DMA"] = nat["Daily_Confirmed"].rolling(7, min_periods=1).mean().round(0)
    nat["Deaths_7DMA"]    = nat["Daily_Deaths"].rolling(7, min_periods=1).mean().round(0)
    nat["Recovery_Rate_Pct"] = (
        nat["Total_Recovered"] / nat["Total_Confirmed"].replace(0, np.nan) * 100
    ).round(2)
    nat["CFR_Pct"] = (
        nat["Total_Deaths"] / nat["Total_Confirmed"].replace(0, np.nan) * 100
    ).round(4)
    nat["Month"] = nat["Date"].dt.to_period("M").astype(str)
    nat["Year"]  = nat["Date"].dt.year
    return nat


def get_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Latest snapshot totals per state — used for bar/ranking charts."""
    latest = (
        df.sort_values("Date")
          .groupby("State")
          .last()
          .reset_index()
    )[["State", "Total_Confirmed", "Total_Recovered", "Total_Deaths",
       "Total_Active", "Recovery_Rate_Pct", "CFR_Pct"]]
    return latest.sort_values("Total_Confirmed", ascending=False).reset_index(drop=True)


def print_summary_stats(df: pd.DataFrame, nat: pd.DataFrame) -> dict:
    """Print & return key headline KPIs."""
    summary = df.groupby("State").last().reset_index()
    kpis = {
        "Total Confirmed": int(summary["Total_Confirmed"].sum()),
        "Total Recovered": int(summary["Total_Recovered"].sum()),
        "Total Deaths":    int(summary["Total_Deaths"].sum()),
        "Active Cases":    int(summary["Total_Active"].sum()),
        "Recovery Rate":   round(summary["Total_Recovered"].sum() /
                                 summary["Total_Confirmed"].sum() * 100, 2),
        "Case Fatality Rate": round(summary["Total_Deaths"].sum() /
                                    summary["Total_Confirmed"].sum() * 100, 4),
        "Peak Daily Cases":   int(nat["Daily_Confirmed"].max()),
        "Peak Date":          str(nat.loc[nat["Daily_Confirmed"].idxmax(), "Date"].date()),
        "States Analysed":    int(df["State"].nunique()),
    }

    print(f"\n{'='*55}")
    print("  📊  INDIA COVID-19 KEY PERFORMANCE INDICATORS")
    print(f"{'='*55}")
    for k, v in kpis.items():
        val_str = f"{v:,}" if isinstance(v, int) else str(v)
        print(f"  {'•'} {k:<26} : {val_str}")
    print(f"{'='*55}\n")
    return kpis
