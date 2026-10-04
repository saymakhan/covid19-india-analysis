"""
COVID-19 India Dataset Generator
Generates realistic synthetic daily state-wise COVID-19 data for India
spanning from Jan 2020 to Dec 2021 (pandemic peak period).
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

STATES = {
    "Maharashtra":    {"peak": 0.14, "delay": 30},
    "Kerala":         {"peak": 0.10, "delay": 20},
    "Karnataka":      {"peak": 0.09, "delay": 45},
    "Tamil Nadu":     {"peak": 0.09, "delay": 35},
    "Andhra Pradesh": {"peak": 0.07, "delay": 40},
    "Delhi":          {"peak": 0.08, "delay": 25},
    "Uttar Pradesh":  {"peak": 0.06, "delay": 50},
    "West Bengal":    {"peak": 0.05, "delay": 55},
    "Rajasthan":      {"peak": 0.04, "delay": 60},
    "Gujarat":        {"peak": 0.05, "delay": 30},
    "Madhya Pradesh": {"peak": 0.04, "delay": 65},
    "Bihar":          {"peak": 0.03, "delay": 70},
    "Haryana":        {"peak": 0.04, "delay": 45},
    "Odisha":         {"peak": 0.03, "delay": 55},
    "Telangana":      {"peak": 0.04, "delay": 40},
    "Punjab":         {"peak": 0.03, "delay": 50},
    "Jharkhand":      {"peak": 0.02, "delay": 75},
    "Assam":          {"peak": 0.02, "delay": 60},
    "Uttarakhand":    {"peak": 0.02, "delay": 55},
    "Himachal Pradesh":{"peak": 0.01,"delay": 65},
    "Goa":            {"peak": 0.01, "delay": 35},
    "Chandigarh":     {"peak": 0.01, "delay": 30},
    "Jammu & Kashmir":{"peak": 0.02, "delay": 60},
    "Chhattisgarh":   {"peak": 0.02, "delay": 70},
    "Tripura":        {"peak": 0.01, "delay": 80},
}

START_DATE = datetime(2020, 1, 30)
END_DATE   = datetime(2021, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days + 1

INDIA_TOTAL_CONFIRMED = 34_800_000
INDIA_TOTAL_DEATHS    = 481_000

records = []

def wave_function(t, n_days):
    """Multi-wave epidemic curve with two peaks (Wave 1 + Delta Wave)."""
    # Wave 1: peak around day 180
    w1 = np.exp(-((t - 180)**2) / (2 * 80**2))
    # Wave 2 (Delta): peak around day 450
    w2 = 1.6 * np.exp(-((t - 450)**2) / (2 * 60**2))
    return (w1 + w2) / (w1 + w2).sum()

t_vals = np.arange(TOTAL_DAYS)
india_daily = wave_function(t_vals, TOTAL_DAYS) * INDIA_TOTAL_CONFIRMED
india_daily = np.maximum(india_daily, 0).astype(int)

for state, cfg in STATES.items():
    proportion = cfg["peak"]
    delay      = cfg["delay"]

    shifted = np.roll(india_daily * proportion, delay)
    shifted[:delay] = 0
    noise = np.random.normal(1.0, 0.08, TOTAL_DAYS)
    state_confirmed = np.maximum((shifted * noise).astype(int), 0)

    recovery_rate = np.random.uniform(0.93, 0.97)
    cfr           = np.random.uniform(0.009, 0.022)

    state_recovered = (state_confirmed * recovery_rate).astype(int)
    state_deaths    = (state_confirmed * cfr).astype(int)
    state_active    = np.maximum(state_confirmed - state_recovered - state_deaths, 0)

    cum_confirmed = np.cumsum(state_confirmed)
    cum_recovered = np.cumsum(state_recovered)
    cum_deaths    = np.cumsum(state_deaths)
    cum_active    = cum_confirmed - cum_recovered - cum_deaths

    for i in range(TOTAL_DAYS):
        date = START_DATE + timedelta(days=i)
        records.append({
            "Date":              date.strftime("%Y-%m-%d"),
            "State":             state,
            "Daily_Confirmed":   int(state_confirmed[i]),
            "Daily_Recovered":   int(state_recovered[i]),
            "Daily_Deaths":      int(state_deaths[i]),
            "Daily_Active":      int(state_active[i]),
            "Total_Confirmed":   int(cum_confirmed[i]),
            "Total_Recovered":   int(cum_recovered[i]),
            "Total_Deaths":      int(cum_deaths[i]),
            "Total_Active":      int(np.maximum(cum_active[i], 0)),
        })

df = pd.DataFrame(records)
df["Date"] = pd.to_datetime(df["Date"])

# Add derived columns
df["Recovery_Rate"] = (df["Total_Recovered"] / df["Total_Confirmed"].replace(0, np.nan) * 100).round(2)
df["CFR"]           = (df["Total_Deaths"]    / df["Total_Confirmed"].replace(0, np.nan) * 100).round(4)

import os
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covid_india_statewise.csv")
df.to_csv(output_path, index=False)
print(f"✅ Dataset generated: {len(df):,} rows × {len(df.columns)} columns")
print(f"   Date range : {df['Date'].min().date()} → {df['Date'].max().date()}")
print(f"   States     : {df['State'].nunique()}")
print(f"   Saved to   : {output_path}")
