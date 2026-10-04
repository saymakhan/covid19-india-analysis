"""
visualizations.py
-----------------
Generates all publication-quality charts for the COVID-19 India report.
Each function saves its figure to the output/ folder and returns the filepath.

Charts produced:
  Fig 01 – National daily case trends (line chart + 7DMA)
  Fig 02 – Top-15 states bar chart (total confirmed)
  Fig 03 – Recovery vs Deaths comparison bar (top 10 states)
  Fig 04 – Monthly new cases heatmap (state × month)
  Fig 05 – Wave progression area chart (Wave 1 vs Wave 2)
  Fig 06 – CFR by state horizontal bar
  Fig 07 – Daily deaths line chart with 7DMA
  Fig 08 – Active cases over time (India)
  Fig 09 – Pie chart: Outcome distribution
  Fig 10 – Recovery rate trend (line) – top 5 states
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns

matplotlib.use("Agg")           # non-interactive backend
warnings.filterwarnings("ignore")

# ── Design System ────────────────────────────────────────────────────────────
PALETTE = {
    "confirmed": "#4FC3F7",   # sky blue
    "recovered": "#66BB6A",   # green
    "deaths":    "#EF5350",   # red
    "active":    "#FFA726",   # amber
    "accent":    "#AB47BC",   # purple
    "bg":        "#0D1117",   # near-black
    "surface":   "#161B22",   # dark card
    "surface2":  "#1C2333",
    "text":      "#E6EDF3",
    "subtext":   "#8B949E",
    "grid":      "#21262D",
    "border":    "#30363D",
}
FONT_FAMILY = "DejaVu Sans"

def _apply_dark_style(fig, ax_list):
    """Apply premium dark theme to any figure."""
    fig.patch.set_facecolor(PALETTE["bg"])
    for ax in (ax_list if isinstance(ax_list, list) else [ax_list]):
        ax.set_facecolor(PALETTE["surface"])
        ax.tick_params(colors=PALETTE["text"], labelsize=9)
        ax.xaxis.label.set_color(PALETTE["text"])
        ax.yaxis.label.set_color(PALETTE["text"])
        ax.title.set_color(PALETTE["text"])
        for spine in ax.spines.values():
            spine.set_edgecolor(PALETTE["border"])
        ax.grid(color=PALETTE["grid"], linestyle="--", linewidth=0.5, alpha=0.7)
        ax.set_axisbelow(True)

def _save(fig, filename: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=PALETTE["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  💾  Saved → {path}")
    return path


def fig01_national_trend(nat: pd.DataFrame, output_dir="output") -> str:
    """Line chart: India daily confirmed + 7DMA ribbon."""
    fig, ax = plt.subplots(figsize=(14, 5))
    _apply_dark_style(fig, ax)

    ax.fill_between(nat["Date"], nat["Daily_Confirmed"],
                    color=PALETTE["confirmed"], alpha=0.15)
    ax.plot(nat["Date"], nat["Daily_Confirmed"],
            color=PALETTE["confirmed"], lw=1, alpha=0.5, label="Daily Confirmed")
    ax.plot(nat["Date"], nat["Confirmed_7DMA"],
            color=PALETTE["confirmed"], lw=2.2, label="7-Day Moving Average")

    # Annotate peak
    peak_idx = nat["Daily_Confirmed"].idxmax()
    peak_val = nat.loc[peak_idx, "Daily_Confirmed"]
    peak_dt  = nat.loc[peak_idx, "Date"]
    ax.annotate(f"Peak\n{peak_val:,.0f}",
                xy=(peak_dt, peak_val),
                xytext=(peak_dt + pd.Timedelta(days=25), peak_val * 0.85),
                fontsize=8, color=PALETTE["confirmed"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["confirmed"], lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", fc=PALETTE["surface2"], ec=PALETTE["confirmed"], lw=0.8))

    # Wave labels
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-01-31"),
               alpha=0.04, color=PALETTE["accent"], label="Wave 1")
    ax.axvspan(pd.Timestamp("2021-03-01"), pd.Timestamp("2021-07-31"),
               alpha=0.07, color="#EF5350", label="Delta Wave")

    ax.set_title("India COVID-19 — Daily Confirmed Cases with 7-Day Moving Average",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Daily Cases", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}K" if x >= 1000 else str(int(x))))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig01_national_trend.png", output_dir)


def fig02_top_states_bar(state_summary: pd.DataFrame, output_dir="output") -> str:
    """Horizontal bar: Top 15 states by total confirmed."""
    top15 = state_summary.head(15).sort_values("Total_Confirmed")
    colors = [PALETTE["confirmed"]] * len(top15)

    fig, ax = plt.subplots(figsize=(11, 7))
    _apply_dark_style(fig, ax)

    bars = ax.barh(top15["State"], top15["Total_Confirmed"], color=colors,
                   edgecolor="none", height=0.65)

    # Gradient effect via alpha
    for i, bar in enumerate(bars):
        bar.set_alpha(0.55 + 0.45 * (i / len(bars)))

    # Value labels
    for bar in bars:
        val = bar.get_width()
        ax.text(val + top15["Total_Confirmed"].max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val/1e6:.2f}M" if val >= 1e6 else f"{val/1e3:.0f}K",
                va="center", ha="left", color=PALETTE["text"], fontsize=8.5)

    ax.set_title("Top 15 States — Total Confirmed COVID-19 Cases",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Total Confirmed Cases", fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
    ax.tick_params(axis="y", labelsize=9.5)
    fig.tight_layout()
    return _save(fig, "fig02_top_states_bar.png", output_dir)


def fig03_recovery_vs_deaths(state_summary: pd.DataFrame, output_dir="output") -> str:
    """Grouped bar: Recovered vs Deaths for top 10 states."""
    top10 = state_summary.head(10)
    x  = np.arange(len(top10))
    w  = 0.38

    fig, ax = plt.subplots(figsize=(13, 5.5))
    _apply_dark_style(fig, ax)

    b1 = ax.bar(x - w/2, top10["Total_Recovered"], w,
                color=PALETTE["recovered"], alpha=0.85, label="Recovered", edgecolor="none")
    b2 = ax.bar(x + w/2, top10["Total_Deaths"], w,
                color=PALETTE["deaths"], alpha=0.85, label="Deaths", edgecolor="none")

    def autolabel(bars, scale="M"):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + top10["Total_Recovered"].max() * 0.01,
                    f"{h/1e6:.2f}M" if h >= 1e6 else f"{h/1e3:.0f}K",
                    ha="center", va="bottom", fontsize=7.5, color=PALETTE["text"])

    autolabel(b1)
    autolabel(b2)

    ax.set_xticks(x)
    ax.set_xticklabels(top10["State"], rotation=22, ha="right", fontsize=9)
    ax.set_title("Top 10 States — Recoveries vs Deaths Comparison",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_ylabel("Total Cases", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig03_recovery_vs_deaths.png", output_dir)


def fig04_monthly_heatmap(df: pd.DataFrame, output_dir="output") -> str:
    """Heatmap: Monthly new cases per state (top 15 states)."""
    top15_states = (
        df.groupby("State")["Total_Confirmed"].max()
          .nlargest(15).index.tolist()
    )
    pivot = (
        df[df["State"].isin(top15_states)]
          .groupby(["State", "Month"])["Daily_Confirmed"]
          .sum()
          .unstack("Month")
          .fillna(0)
    )
    pivot = pivot.reindex(
        df[df["State"].isin(top15_states)]
          .groupby("State")["Total_Confirmed"].max()
          .sort_values(ascending=False).index
    )

    fig, ax = plt.subplots(figsize=(18, 7))
    _apply_dark_style(fig, ax)

    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    sns.heatmap(
        pivot / 1000,
        ax=ax, cmap=cmap, linewidths=0.3, linecolor=PALETTE["bg"],
        fmt=".0f", annot=True, annot_kws={"size": 6.5},
        cbar_kws={"label": "New Cases (thousands)", "shrink": 0.7},
    )
    ax.set_facecolor(PALETTE["surface"])
    ax.set_title("Monthly COVID-19 New Cases by State (in Thousands)",
                 fontsize=13, fontweight="bold", pad=14, color=PALETTE["text"])
    ax.set_xlabel("Month", fontsize=10, color=PALETTE["text"])
    ax.set_ylabel("State", fontsize=10, color=PALETTE["text"])
    ax.tick_params(axis="x", rotation=45, labelsize=7.5, colors=PALETTE["text"])
    ax.tick_params(axis="y", rotation=0,  labelsize=8.5, colors=PALETTE["text"])
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=PALETTE["text"])
    cbar.set_label("New Cases (thousands)", color=PALETTE["text"])
    fig.tight_layout()
    return _save(fig, "fig04_monthly_heatmap.png", output_dir)


def fig05_wave_area(nat: pd.DataFrame, output_dir="output") -> str:
    """Stacked area: Active vs Recovered vs Deaths over time."""
    fig, ax = plt.subplots(figsize=(14, 5.5))
    _apply_dark_style(fig, ax)

    ax.stackplot(
        nat["Date"],
        nat["Daily_Active"].clip(0),
        nat["Daily_Recovered"],
        nat["Daily_Deaths"],
        labels=["Active", "Recovered", "Deaths"],
        colors=[PALETTE["active"], PALETTE["recovered"], PALETTE["deaths"]],
        alpha=0.75,
    )

    ax.set_title("India — Daily Case Outcome Stack (Active / Recovered / Deaths)",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Daily Cases", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}K" if x >= 1000 else str(int(x))))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9, loc="upper left")
    fig.tight_layout()
    return _save(fig, "fig05_wave_area.png", output_dir)


def fig06_cfr_bar(state_summary: pd.DataFrame, output_dir="output") -> str:
    """Horizontal bar: CFR % by state (top 20)."""
    top20 = state_summary.nlargest(20, "Total_Confirmed").sort_values("CFR_Pct")

    norm  = plt.Normalize(top20["CFR_Pct"].min(), top20["CFR_Pct"].max())
    cmap  = plt.cm.RdYlGn_r
    colors = [cmap(norm(v)) for v in top20["CFR_Pct"]]

    fig, ax = plt.subplots(figsize=(11, 7))
    _apply_dark_style(fig, ax)

    bars = ax.barh(top20["State"], top20["CFR_Pct"], color=colors,
                   edgecolor="none", height=0.65)
    for bar in bars:
        val = bar.get_width()
        ax.text(val + 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}%", va="center", ha="left",
                color=PALETTE["text"], fontsize=8.5)

    ax.axvline(x=top20["CFR_Pct"].mean(), color="#FFA726", lw=1.5,
               linestyle="--", alpha=0.8, label=f"Avg CFR = {top20['CFR_Pct'].mean():.2f}%")
    ax.set_title("Case Fatality Rate (CFR %) by State",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("CFR (%)", fontsize=10)
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig06_cfr_bar.png", output_dir)


def fig07_daily_deaths(nat: pd.DataFrame, output_dir="output") -> str:
    """Line chart: Daily deaths + 7DMA with gradient fill."""
    fig, ax = plt.subplots(figsize=(14, 4.5))
    _apply_dark_style(fig, ax)

    ax.fill_between(nat["Date"], nat["Daily_Deaths"],
                    color=PALETTE["deaths"], alpha=0.12)
    ax.plot(nat["Date"], nat["Daily_Deaths"],
            color=PALETTE["deaths"], lw=1, alpha=0.45, label="Daily Deaths")
    ax.plot(nat["Date"], nat["Deaths_7DMA"],
            color=PALETTE["deaths"], lw=2.2, label="7-Day Moving Average")

    peak_idx = nat["Daily_Deaths"].idxmax()
    peak_val = nat.loc[peak_idx, "Daily_Deaths"]
    peak_dt  = nat.loc[peak_idx, "Date"]
    ax.annotate(f"Peak Deaths\n{peak_val:,.0f}/day",
                xy=(peak_dt, peak_val),
                xytext=(peak_dt + pd.Timedelta(days=20), peak_val * 0.82),
                fontsize=8, color=PALETTE["deaths"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["deaths"], lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", fc=PALETTE["surface2"], ec=PALETTE["deaths"], lw=0.8))

    ax.set_title("India — Daily COVID-19 Deaths with 7-Day Moving Average",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Daily Deaths", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig07_daily_deaths.png", output_dir)


def fig08_active_cases(nat: pd.DataFrame, output_dir="output") -> str:
    """Area chart: Active cases over time India."""
    fig, ax = plt.subplots(figsize=(14, 4.5))
    _apply_dark_style(fig, ax)

    ax.fill_between(nat["Date"], nat["Total_Active"].clip(0),
                    color=PALETTE["active"], alpha=0.25)
    ax.plot(nat["Date"], nat["Total_Active"].clip(0),
            color=PALETTE["active"], lw=2, label="Active Cases")

    ax.set_title("India — Total Active Cases Over Time",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Active Cases", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else (f"{x/1e3:.0f}K" if x >= 1000 else str(int(x)))))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig08_active_cases.png", output_dir)


def fig09_outcome_pie(state_summary: pd.DataFrame, output_dir="output") -> str:
    """Donut chart: Outcome distribution (Recovered / Active / Deaths)."""
    totals = state_summary[["Total_Recovered", "Total_Active", "Total_Deaths"]].sum()
    labels = ["Recovered", "Active", "Deaths"]
    colors = [PALETTE["recovered"], PALETTE["active"], PALETTE["deaths"]]
    sizes  = totals.values

    fig, ax = plt.subplots(figsize=(7, 7))
    _apply_dark_style(fig, ax)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=colors,
        autopct="%1.1f%%", startangle=140,
        pctdistance=0.78, wedgeprops=dict(width=0.52, edgecolor=PALETTE["bg"], linewidth=2),
    )
    for at in autotexts:
        at.set_color(PALETTE["bg"])
        at.set_fontweight("bold")
        at.set_fontsize(11)

    ax.legend(wedges, [f"{l}  ({v/1e6:.2f}M)" for l, v in zip(labels, sizes)],
              loc="lower center", ncol=3,
              facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9,
              bbox_to_anchor=(0.5, -0.05))
    ax.set_title("India COVID-19 — Case Outcome Distribution",
                 fontsize=13, fontweight="bold", pad=18, color=PALETTE["text"])
    ax.text(0, 0, "INDIA\nCOVID-19", ha="center", va="center",
            fontsize=11, fontweight="bold", color=PALETTE["text"], linespacing=1.8)
    fig.tight_layout()
    return _save(fig, "fig09_outcome_pie.png", output_dir)


def fig10_recovery_rate_trend(df: pd.DataFrame, output_dir="output") -> str:
    """Line chart: 30-day rolling recovery rate for top 5 states."""
    top5 = (
        df.groupby("State")["Total_Confirmed"].max()
          .nlargest(5).index.tolist()
    )
    state_colors = [PALETTE["confirmed"], PALETTE["recovered"],
                    PALETTE["deaths"], PALETTE["active"], PALETTE["accent"]]

    fig, ax = plt.subplots(figsize=(14, 5))
    _apply_dark_style(fig, ax)

    for state, color in zip(top5, state_colors):
        sdf = df[df["State"] == state].copy()
        sdf["RR_30D"] = (
            sdf["Total_Recovered"] / sdf["Total_Confirmed"].replace(0, np.nan) * 100
        ).rolling(30, min_periods=1).mean()
        ax.plot(sdf["Date"], sdf["RR_30D"], lw=2, label=state, color=color)

    ax.set_title("30-Day Rolling Recovery Rate — Top 5 Most Affected States",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Recovery Rate (%)", fontsize=10)
    ax.set_ylim(0, 105)
    ax.axhline(y=95, color=PALETTE["subtext"], lw=1, linestyle="--", alpha=0.5, label="95% Benchmark")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=PALETTE["surface2"], edgecolor=PALETTE["border"],
              labelcolor=PALETTE["text"], fontsize=9, ncol=3)
    fig.tight_layout()
    return _save(fig, "fig10_recovery_rate.png", output_dir)


def generate_all(df, nat, state_summary, output_dir="output") -> list:
    """Run all 10 figure generators and return list of saved paths."""
    print(f"\n{'='*55}")
    print("  🎨  Generating Visualizations")
    print(f"{'='*55}")
    paths = [
        fig01_national_trend(nat, output_dir),
        fig02_top_states_bar(state_summary, output_dir),
        fig03_recovery_vs_deaths(state_summary, output_dir),
        fig04_monthly_heatmap(df, output_dir),
        fig05_wave_area(nat, output_dir),
        fig06_cfr_bar(state_summary, output_dir),
        fig07_daily_deaths(nat, output_dir),
        fig08_active_cases(nat, output_dir),
        fig09_outcome_pie(state_summary, output_dir),
        fig10_recovery_rate_trend(df, output_dir),
    ]
    print(f"\n  ✅  {len(paths)} charts generated successfully!\n")
    return paths
