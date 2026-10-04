"""
main.py — COVID-19 India Data Analysis Pipeline
================================================
Orchestrates all stages of the analysis:

  Stage 1: Generate dataset (if not already present)
  Stage 2: Load & clean data
  Stage 3: Compute summary statistics / KPIs
  Stage 4: Generate all 10 visualisations
  Stage 5: Produce automated PDF report

Run:
    py main.py
    py main.py --no-pdf      (skip PDF generation)
    py main.py --regen-data  (force regenerate CSV)
"""

import os
import sys
import argparse
import subprocess

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_FILE   = os.path.join(BASE_DIR, "data", "covid_india_statewise.csv")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def _banner():
    print("\n" + "=" * 55)
    print("   COVID-19 INDIA DATA ANALYSIS PIPELINE")
    print("   Python | Pandas | Matplotlib | Seaborn | FPDF")
    print("=" * 55)


def _ensure_data(regen: bool = False):
    """Generate the dataset CSV if it doesn't exist (or regen=True)."""
    if regen or not os.path.exists(DATA_FILE):
        print("\n  ⚙️   Generating synthetic COVID-19 dataset …")
        gen_script = os.path.join(BASE_DIR, "data", "generate_data.py")
        result = subprocess.run([sys.executable, gen_script], check=True)
        if result.returncode != 0:
            raise RuntimeError("Dataset generation failed.")
    else:
        print(f"\n  📁  Dataset found: {DATA_FILE}")


def main():
    parser = argparse.ArgumentParser(description="COVID-19 India Analysis Pipeline")
    parser.add_argument("--no-pdf",      action="store_true", help="Skip PDF report generation")
    parser.add_argument("--regen-data",  action="store_true", help="Regenerate CSV dataset")
    args = parser.parse_args()

    _banner()

    # ── Stage 1: Data ─────────────────────────────────────────────────────────
    _ensure_data(regen=args.regen_data)

    # ── Stage 2: Load & Clean ─────────────────────────────────────────────────
    from data_loader import load_data, get_national_daily, get_state_summary, print_summary_stats
    df           = load_data(DATA_FILE)
    nat          = get_national_daily(df)
    state_summary = get_state_summary(df)
    kpis         = print_summary_stats(df, nat)

    # ── Stage 3: Visualisations ───────────────────────────────────────────────
    from visualizations import generate_all
    chart_paths = generate_all(df, nat, state_summary, output_dir=OUTPUT_DIR)

    # ── Stage 4: PDF Report ───────────────────────────────────────────────────
    if not args.no_pdf:
        print(f"\n{'='*55}")
        print("  📝  Generating PDF Report")
        print(f"{'='*55}")
        from pdf_report import generate_report
        pdf_path = generate_report(kpis, chart_paths, output_dir=REPORTS_DIR)
    else:
        pdf_path = None
        print("\n  ⏩  PDF generation skipped (--no-pdf flag).")

    # ── Done ──────────────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("   ANALYSIS COMPLETE")
    print("=" * 55)
    print(f"  Charts  ->  {OUTPUT_DIR}")
    if pdf_path:
        print(f"  Report  ->  {pdf_path}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
