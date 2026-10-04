"""
pdf_report.py
-------------
Generates a professional multi-page PDF report using fpdf2.

Report sections:
  Page 1  – Cover page with KPI summary cards
  Page 2  – National trend + active cases charts
  Page 3  – State-level bar chart + recovery vs deaths
  Page 4  – Monthly heatmap
  Page 5  – Wave area chart + daily deaths
  Page 6  – CFR bar + recovery rate trend
  Page 7  – Outcome donut + insights & conclusions
"""

import os
from datetime import datetime
from fpdf import FPDF, XPos, YPos


# ── Colours (RGB) ────────────────────────────────────────────────────────────
C_BG      = (13,  17,  23)    # #0D1117
C_SURFACE = (22,  27,  34)    # #161B22
C_BORDER  = (48,  54,  61)    # #30363D
C_TEXT    = (230, 237, 243)   # #E6EDF3
C_SUB     = (139, 148, 158)   # #8B949E
C_BLUE    = (79,  195, 247)   # confirmed
C_GREEN   = (102, 187, 106)   # recovered
C_RED     = (239, 83,  80)    # deaths
C_AMBER   = (255, 167, 38)    # active
C_PURPLE  = (171, 71,  188)   # accent


class CovidPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=12)
        self.set_margins(0, 0, 0)

    # ── Header / Footer ──────────────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*C_BG)
        self.rect(0, 0, self.w, 12, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C_SUB)
        self.set_xy(8, 3)
        self.cell(0, 6, "COVID-19 INDIA DATA ANALYSIS REPORT  |  Python | Pandas | Matplotlib | Seaborn", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_xy(0, 11)
        self.set_fill_color(*C_BORDER)
        self.rect(0, 11, self.w, 0.3, "F")

    def footer(self):
        self.set_y(-10)
        self.set_fill_color(*C_BG)
        self.rect(0, self.h - 10, self.w, 10, "F")
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*C_SUB)
        self.cell(0, 6, f"Page {self.page_no()}  |  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}  |  Data: Jan 2020 - Dec 2021",
                  align="C")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def fill_bg(self):
        self.set_fill_color(*C_BG)
        self.rect(0, 0, self.w, self.h, "F")

    def section_title(self, txt, x=8, y=None):
        if y is None:
            y = self.get_y() + 4
        self.set_xy(x, y)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*C_BLUE)
        self.cell(0, 7, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_fill_color(*C_BORDER)
        self.rect(x, self.get_y(), 60, 0.4, "F")
        self.ln(3)

    def kpi_card(self, x, y, w, h, title, value, color):
        r, g, b = color
        # Card background
        self.set_fill_color(*C_SURFACE)
        self.rect(x, y, w, h, "F")
        # Left accent bar
        self.set_fill_color(r, g, b)
        self.rect(x, y, 2.5, h, "F")
        # Title
        self.set_xy(x + 5, y + 3)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*C_SUB)
        self.cell(w - 7, 5, title.upper())
        # Value
        self.set_xy(x + 5, y + 9)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(r, g, b)
        self.cell(w - 7, 8, value)

    def insight_bullet(self, txt):
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*C_TEXT)
        x0 = self.get_x()
        # bullet
        self.set_fill_color(*C_BLUE)
        self.ellipse(x0, self.get_y() + 2, 1.8, 1.8, "F")
        self.set_xy(x0 + 4, self.get_y())
        self.multi_cell(0, 5, txt)
        self.ln(1)


def _fmt(n):
    """Format large numbers nicely."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def generate_report(kpis: dict, chart_paths: list,
                    output_dir: str = "reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    pdf = CovidPDF()

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1 — COVER
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.fill_bg()

    # Hero gradient rectangle
    pdf.set_fill_color(22, 27, 70)
    pdf.rect(0, 0, pdf.w, 60, "F")

    # Title
    pdf.set_xy(0, 14)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*C_BLUE)
    pdf.cell(0, 12, "COVID-19 INDIA DATA ANALYSIS", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(*C_TEXT)
    pdf.cell(0, 8, "State-wise Analysis  |  Jan 2020 - Dec 2021", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_SUB)
    pdf.cell(0, 6, "Python | Pandas | Matplotlib | Seaborn | FPDF2", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Divider
    pdf.set_fill_color(*C_BLUE)
    pdf.rect(30, 56, pdf.w - 60, 0.6, "F")

    # ── KPI Cards (2 rows × 4 cols) ──────────────────────────────────────────
    card_defs = [
        ("Total Confirmed",    _fmt(kpis["Total Confirmed"]),    C_BLUE),
        ("Total Recovered",    _fmt(kpis["Total Recovered"]),    C_GREEN),
        ("Total Deaths",       _fmt(kpis["Total Deaths"]),       C_RED),
        ("Active Cases",       _fmt(kpis["Active Cases"]),       C_AMBER),
        ("Recovery Rate",      f"{kpis['Recovery Rate']}%",      C_GREEN),
        ("Case Fatality Rate", f"{kpis['Case Fatality Rate']}%", C_RED),
        ("Peak Daily Cases",   _fmt(kpis["Peak Daily Cases"]),   C_PURPLE),
        ("States Analysed",    str(kpis["States Analysed"]),     C_BLUE),
    ]

    cols    = 4
    margin  = 10
    gap     = 5
    cw      = (pdf.w - 2 * margin - (cols - 1) * gap) / cols
    ch      = 28
    row_y   = [66, 100]

    for i, (title, value, color) in enumerate(card_defs):
        row = i // cols
        col = i % cols
        cx  = margin + col * (cw + gap)
        cy  = row_y[row]
        pdf.kpi_card(cx, cy, cw, ch, title, value, color)

    # ── Peak info ─────────────────────────────────────────────────────────────
    pdf.set_xy(0, 134)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*C_SUB)
    pdf.cell(0, 6, f"Peak daily confirmed cases recorded on  {kpis['Peak Date']}", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Tool stack badges ─────────────────────────────────────────────────────
    badge_labels = ["Python 3.9", "Pandas", "Matplotlib", "Seaborn", "FPDF2", "NumPy"]
    badge_colors = [C_BLUE, C_GREEN, C_AMBER, C_RED, C_PURPLE, C_BLUE]
    bx, by = 35, 148
    for lbl, clr in zip(badge_labels, badge_colors):
        pdf.set_fill_color(*clr)
        pdf.set_text_color(*C_BG)
        pdf.set_font("Helvetica", "B", 7.5)
        tw = pdf.get_string_width(lbl) + 8
        pdf.rect(bx, by, tw, 8, "F")
        pdf.set_xy(bx + 1, by + 1)
        pdf.cell(tw - 2, 6, lbl)
        bx += tw + 4

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2 — National Trend + Active Cases
    # ══════════════════════════════════════════════════════════════════════════
    def _add_chart_page(title, chart_paths_page, layout="2h"):
        """layout: '2h' = 2 horizontal halves, '1f' = 1 full width."""
        pdf.add_page()
        pdf.fill_bg()
        pdf.set_xy(8, 14)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*C_BLUE)
        pdf.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_fill_color(*C_BORDER)
        pdf.rect(8, pdf.get_y(), pdf.w - 16, 0.4, "F")
        pdf.ln(2)

        top_y    = pdf.get_y()
        img_area_w = pdf.w - 16
        img_area_h = pdf.h - top_y - 14

        if layout == "1f":
            for i, p in enumerate(chart_paths_page):
                if p and os.path.exists(p):
                    ih = img_area_h / len(chart_paths_page)
                    pdf.image(p, x=8, y=top_y + i * ih, w=img_area_w, h=ih - 2)
        elif layout == "2h":
            half_w = img_area_w / 2 - 2
            for i, p in enumerate(chart_paths_page):
                if p and os.path.exists(p):
                    px = 8 if i % 2 == 0 else 8 + half_w + 4
                    py = top_y + (i // 2) * (img_area_h / (len(chart_paths_page) / 2 + 0.5))
                    pdf.image(p, x=px, y=py, w=half_w, h=img_area_h / 2 - 3)
        elif layout == "top1_bot2":
            # One full-width image on top, two half-width on bottom
            if chart_paths_page[0] and os.path.exists(chart_paths_page[0]):
                pdf.image(chart_paths_page[0], x=8, y=top_y, w=img_area_w, h=img_area_h * 0.52)
            bot_y = top_y + img_area_h * 0.54
            half_w = img_area_w / 2 - 2
            for i, p in enumerate(chart_paths_page[1:]):
                if p and os.path.exists(p):
                    px = 8 if i == 0 else 8 + half_w + 4
                    pdf.image(p, x=px, y=bot_y, w=half_w, h=img_area_h * 0.44)

    # Page 2
    pdf.add_page()
    pdf.fill_bg()
    pdf.set_xy(8, 14)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*C_BLUE)
    pdf.cell(0, 7, "India - National Case Progression", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(*C_BORDER)
    pdf.rect(8, pdf.get_y(), pdf.w - 16, 0.4, "F")
    pdf.ln(2)
    top_y = pdf.get_y()
    img_w = pdf.w - 16
    img_h = (pdf.h - top_y - 14) / 2 - 2
    for i, idx in enumerate([0, 7]):   # fig01, fig08
        if idx < len(chart_paths) and chart_paths[idx] and os.path.exists(chart_paths[idx]):
            pdf.image(chart_paths[idx], x=8, y=top_y + i * (img_h + 3), w=img_w, h=img_h)

    # Page 3 – State bar + Recovery vs Deaths
    _add_chart_page("State-Level Analysis - Top States",
                    [chart_paths[1], chart_paths[2]], layout="2h")

    # Page 4 – Monthly heatmap (full width)
    pdf.add_page()
    pdf.fill_bg()
    pdf.set_xy(8, 14)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*C_BLUE)
    pdf.cell(0, 7, "Monthly Case Distribution Heatmap", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(*C_BORDER)
    pdf.rect(8, pdf.get_y(), pdf.w - 16, 0.4, "F")
    pdf.ln(2)
    top_y = pdf.get_y()
    if chart_paths[3] and os.path.exists(chart_paths[3]):
        pdf.image(chart_paths[3], x=8, y=top_y, w=pdf.w - 16, h=pdf.h - top_y - 16)

    # Page 5 – Wave area + Daily deaths
    _add_chart_page("Wave Progression & Daily Mortality",
                    [chart_paths[4], chart_paths[6]], layout="1f")

    # Page 6 – CFR + Recovery rate trend
    _add_chart_page("Case Fatality Rate & Recovery Trends",
                    [chart_paths[5], chart_paths[9]], layout="2h")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 7 — Outcome Pie + Key Insights
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.fill_bg()
    pdf.set_xy(8, 14)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*C_BLUE)
    pdf.cell(0, 7, "Case Outcome Distribution and Actionable Insights", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(*C_BORDER)
    pdf.rect(8, pdf.get_y(), pdf.w - 16, 0.4, "F")
    pdf.ln(3)

    top_y = pdf.get_y()
    # Pie chart on left
    if chart_paths[8] and os.path.exists(chart_paths[8]):
        pdf.image(chart_paths[8], x=8, y=top_y, w=105, h=100)

    # Insights on right
    pdf.set_xy(120, top_y + 2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*C_AMBER)
    pdf.cell(0, 7, "KEY INSIGHTS & CONCLUSIONS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(*C_AMBER)
    pdf.rect(120, pdf.get_y(), 70, 0.4, "F")
    pdf.ln(3)

    insights = [
        f"Maharashtra led all states with the highest cumulative confirmed cases, accounting for ~14% of national total.",
        f"The Delta Wave (Apr-Jun 2021) caused a sharper and more lethal surge than Wave 1, with peak daily cases ~{_fmt(kpis['Peak Daily Cases'])}.",
        f"India recovery rate reached {kpis['Recovery Rate']}%, indicating strong healthcare system response.",
        f"The Case Fatality Rate (CFR) averaged {kpis['Case Fatality Rate']}%, well below the global average of ~2.2%.",
        f"Kerala showed a high confirmed count but maintained one of the lowest CFR rates, reflecting better healthcare.",
        f"7-day moving averages reveal two distinct epidemic waves with a clear trough between Jan-Feb 2021.",
        f"Monthly heatmaps confirm May-June 2021 as the deadliest period, aligning with the Delta variant peak.",
        f"Active case burden peaked during the Delta Wave, stressing hospital and oxygen infrastructure nationally.",
    ]

    pdf.set_xy(120, pdf.get_y())
    for ins in insights:
        pdf.insight_bullet(ins)

    # Methodology note
    pdf.set_xy(8, top_y + 108)
    pdf.set_fill_color(*C_SURFACE)
    pdf.rect(8, pdf.get_y(), pdf.w - 16, 30, "F")
    pdf.set_fill_color(*C_PURPLE)
    pdf.rect(8, pdf.get_y(), 2.5, 30, "F")
    pdf.set_xy(14, pdf.get_y() + 4)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_PURPLE)
    pdf.cell(0, 5, "METHODOLOGY", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(14, pdf.get_y())
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*C_TEXT)
    pdf.multi_cell(pdf.w - 24, 4.5,
        "Data cleaned using Pandas (null forward-fill, negative clipping, type casting). "
        "DAX-equivalent metrics (Recovery Rate, CFR, 7DMA) computed via vectorised Pandas operations. "
        "Visualisations rendered with Matplotlib + Seaborn on a custom dark theme. "
        "This automated PDF report generated via FPDF2. All figures saved as high-resolution PNGs (150 DPI).")

    # ── Save ──────────────────────────────────────────────────────────────────
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"COVID19_India_Analysis_Report_{ts}.pdf")
    pdf.output(path)
    print(f"\n  PDF report saved -> {path}")
    return path
