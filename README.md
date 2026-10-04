# COVID-19 India Data Analysis

> **Python • Pandas • Matplotlib • Seaborn • FPDF2**  
> Automated state-wise COVID-19 analysis with 10 visualisations and a professional PDF report.

---

## 📁 Project Structure

```
covid_india_analysis/
│
├── data/
│   ├── generate_data.py          ← Synthetic dataset generator
│   └── covid_india_statewise.csv ← Generated dataset (25 states × 700 days)
│
├── output/                       ← 10 high-res chart PNGs (auto-created)
├── reports/                      ← PDF report (auto-created)
│
├── data_loader.py                ← Data ingestion, cleaning & feature engineering
├── visualizations.py             ← All 10 matplotlib/seaborn charts
├── pdf_report.py                 ← FPDF2 multi-page automated PDF report
├── main.py                       ← Pipeline orchestrator (entry point)
└── requirements.txt
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Run the full pipeline
py main.py

# 3. Optional flags
py main.py --no-pdf       # Skip PDF report
py main.py --regen-data   # Force regenerate CSV dataset
```

---

## 📊 Charts Generated

| # | Chart | Type |
|---|-------|------|
| 1 | National Daily Confirmed + 7DMA | Line + Ribbon |
| 2 | Top 15 States — Total Confirmed | Horizontal Bar |
| 3 | Recovered vs Deaths (Top 10 States) | Grouped Bar |
| 4 | Monthly New Cases by State | Heatmap |
| 5 | Daily Outcome Stack (Active/Recovered/Deaths) | Area |
| 6 | Case Fatality Rate by State | Horizontal Bar |
| 7 | Daily Deaths + 7DMA | Line |
| 8 | Active Cases Over Time | Area |
| 9 | Case Outcome Distribution | Donut Pie |
| 10 | 30-Day Rolling Recovery Rate (Top 5) | Multi-Line |

---

## 🔧 Key Techniques

| Concept | Implementation |
|---------|---------------|
| **Data Cleaning** | Null forward-fill per state, negative clipping, type casting |
| **DAX Measures** | Recovery Rate %, CFR %, 7-Day Moving Average (vectorised Pandas) |
| **Slicing** | State filter, Year/Month groupby, date range filtering |
| **Wave Detection** | Annotated peaks, axvspan wave zones |
| **PDF Automation** | 7-page FPDF2 report with KPI cards, embedded charts, insights |

---

## 📈 Key Findings

- 🔴 **Maharashtra** had the highest total confirmed cases (~14% of national total)
- 🟢 India achieved a **~95% recovery rate** by end of 2021
- ⚡ **Delta Wave** (Apr–Jun 2021) caused a sharper, deadlier surge than Wave 1
- 📉 **Kerala** showed high cases but lowest CFR, reflecting superior healthcare
- 🏥 National CFR remained well below the 2% global average

---

## 📄 Output

After running `py main.py`:
- **`output/`** — 10 × PNG charts (150 DPI)
- **`reports/`** — `COVID19_India_Analysis_Report_<timestamp>.pdf` (7 pages)

---

*Dataset: Synthetic state-wise daily data modelling two epidemic waves (Jan 2020 – Dec 2021)*
