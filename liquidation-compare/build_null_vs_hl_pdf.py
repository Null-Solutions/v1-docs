#!/usr/bin/env python3
"""Build PDF: Null liquidation vs Hyperliquid-style maintenance margin."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent
PDF_PATH = OUT_DIR / "null-liquidation-vs-hyperliquid.pdf"
CHART_PATH = OUT_DIR / "liq-drop-vs-leverage.png"
OLD_PDF_PATH = OUT_DIR / "null-liquidation-vs-hyperliquid-10x-alts.pdf"

# Candidate Null LLTVs to compare
LLTVS = [0.915, 0.93, 0.95, 0.97, 0.99, 1.00]
NULL_CURRENT_LLTV = 0.915

# Hyperliquid-style: for a venue with max leverage M, mm = 1/(2M)
HL_MAX_LEV_10 = 10.0
HL_MM_10 = 1.0 / (2.0 * HL_MAX_LEV_10)  # 5%
HL_EFF_LLTV_10 = 1.0 - HL_MM_10  # 95%

HL_MAX_LEV_20 = 20.0
HL_MM_20 = 1.0 / (2.0 * HL_MAX_LEV_20)  # 2.5%
HL_EFF_LLTV_20 = 1.0 - HL_MM_20  # 97.5%

HL_MAX_LEV_50 = 50.0
HL_MM_50 = 1.0 / (2.0 * HL_MAX_LEV_50)  # 1%
HL_EFF_LLTV_50 = 1.0 - HL_MM_50  # 99%

# Leverages of interest for tables / markers
FOCUS_LEVERAGES = [5.0, 10.0, 20.0, 25.0, 40.0, 50.0]


def open_ltv(leverage: float) -> float:
    return 1.0 - 1.0 / leverage


def drop_to_liq(leverage: float, lltv: float) -> float | None:
    """Fraction price can fall before Morpho-style LTV hits LLTV."""
    ol = open_ltv(leverage)
    if lltv <= 0 or ol >= lltv:
        return None
    return 1.0 - ol / lltv


def min_lltv_to_open(leverage: float) -> float:
    """Strict lower bound: need LLTV > open LTV = 1 − 1/L."""
    return open_ltv(leverage)


def max_leverage(lltv: float) -> float | None:
    """Theoretical max lev at full open LTV when LLTV is the ceiling."""
    if lltv >= 1.0:
        return None  # unbounded in the formula; zero-equity limit
    if lltv <= 0:
        return None
    return 1.0 / (1.0 - lltv)


def hl_mm_for_max_lev(max_lev: float) -> float:
    return 1.0 / (2.0 * max_lev)


def hl_eff_lltv(max_lev: float) -> float:
    return 1.0 - hl_mm_for_max_lev(max_lev)


def lltv_to_match_drop(leverage: float, target_drop: float) -> float | None:
    """LLTV such that drop_to_liq(L, LLTV) = target_drop.

    drop = 1 − ol/lltv  ⇒  lltv = ol / (1 − target_drop)
    """
    if target_drop >= 1.0 or target_drop < 0:
        return None
    ol = open_ltv(leverage)
    denom = 1.0 - target_drop
    if denom <= 0:
        return None
    return ol / denom


def fmt_pct(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "—"
    return f"{100.0 * x:.{digits}f}%"


def fmt_lev(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "∞ (limit)"
    if abs(x - round(x)) < 1e-9:
        return f"{int(round(x))}×"
    return f"{x:.{digits}f}×"


def build_chart() -> None:
    leverages = np.linspace(2.0, 55.0, 600)
    palette = {
        0.915: "#1a365d",
        0.93: "#2b6cb0",
        0.95: "#2f855a",
        0.97: "#b7791f",
        0.99: "#c05621",
        1.00: "#9b2c2c",
    }
    labels = {
        0.915: "Null LLTV 91.5% (current)",
        0.93: "Null LLTV 93%",
        0.95: "Null LLTV 95% (= HL 10x-max mm)",
        0.97: "Null LLTV 97%",
        0.99: "Null LLTV 99% (= HL 50x-max mm)",
        1.00: "Null LLTV 100% (zero-equity)",
    }

    fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=160)
    fig.patch.set_facecolor("#fafafa")
    ax.set_facecolor("#fafafa")

    for lltv in LLTVS:
        ys = []
        for L in leverages:
            d = drop_to_liq(float(L), lltv)
            ys.append(None if d is None else 100.0 * d)
        ax.plot(
            leverages,
            ys,
            color=palette[lltv],
            linewidth=2.2 if lltv == NULL_CURRENT_LLTV else 1.6,
            label=labels[lltv],
            zorder=3 if lltv == NULL_CURRENT_LLTV else 2,
        )

    # HL references: 10x-max (mm 5%), 20x-max (mm 2.5%), 50x-max (mm 1%)
    hl_refs = [
        (HL_EFF_LLTV_10, "#718096", "--", "HL 10×-max (mm 5% ≡ LLTV 95%)"),
        (HL_EFF_LLTV_20, "#805ad5", "-.", "HL 20×-max (mm 2.5% ≡ LLTV 97.5%)"),
        (HL_EFF_LLTV_50, "#d53f8c", ":", "HL 50×-max (mm 1% ≡ LLTV 99%)"),
    ]
    for eff, color, ls, label in hl_refs:
        hl_ys = [
            None if (d := drop_to_liq(float(L), eff)) is None else 100.0 * d
            for L in leverages
        ]
        ax.plot(
            leverages,
            hl_ys,
            color=color,
            linewidth=1.8,
            linestyle=ls,
            label=label,
            zorder=4,
        )

    mark_levs = [5.0, 10.0, 20.0, 50.0]
    for L_mark in mark_levs:
        d_null = drop_to_liq(L_mark, NULL_CURRENT_LLTV)
        if d_null is not None:
            ax.scatter([L_mark], [100 * d_null], color="#1a365d", s=32, zorder=5)
            ax.annotate(
                f"{100 * d_null:.1f}%",
                (L_mark, 100 * d_null),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=7,
                color="#1a365d",
            )
        ax.axvline(L_mark, color="#e2e8f0", linewidth=0.9, linestyle=":")

    ax.set_xlabel("Leverage (×)", fontsize=10)
    ax.set_ylabel("Price drop to liquidation (%)", fontsize=10)
    ax.set_title(
        "Liquidation cushion vs leverage: Null Morpho loop vs HL-style mm",
        fontsize=11,
        pad=10,
    )
    ax.set_xlim(2, 55)
    ax.set_ylim(0, 55)
    ax.grid(True, alpha=0.35, linewidth=0.6)
    ax.legend(loc="upper right", fontsize=6.8, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(CHART_PATH, bbox_inches="tight")
    plt.close(fig)


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=colors.HexColor("#1a202c"),
            spaceAfter=6,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            textColor=colors.HexColor("#4a5568"),
            spaceAfter=16,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            textColor=colors.HexColor("#1a365d"),
            spaceBefore=12,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#2c5282"),
            spaceBefore=10,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "BulletCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#2d3748"),
            leftIndent=14,
            spaceAfter=4,
        ),
        "note": ParagraphStyle(
            "NoteCustom",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#4a5568"),
            spaceBefore=3,
            spaceAfter=7,
        ),
        "formula": ParagraphStyle(
            "Formula",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=8,
            leading=11.5,
            textColor=colors.HexColor("#1a202c"),
            backColor=colors.HexColor("#edf2f7"),
            borderPadding=5,
            spaceBefore=3,
            spaceAfter=7,
            alignment=TA_LEFT,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#718096"),
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=8,
        ),
        "th": ParagraphStyle(
            "TH",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "td": ParagraphStyle(
            "TD",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_CENTER,
        ),
        "td_em": ParagraphStyle(
            "TDEm",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#1a365d"),
            alignment=TA_CENTER,
        ),
        "td_warn": ParagraphStyle(
            "TDWarn",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#c53030"),
            alignment=TA_CENTER,
        ),
    }
    return styles


def styled_table(rows: list, col_widths: list, emphasize_rows: set[int] | None = None) -> Table:
    emphasize_rows = emphasize_rows or set()
    t = Table(rows, colWidths=col_widths, hAlign="CENTER")
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#a0aec0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(rows)):
        if i in emphasize_rows:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#ebf4ff")))
        elif i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f7fafc")))
    t.setStyle(TableStyle(style_cmds))
    return t


def comparison_table(leverage: float, styles, hl_ref_lltv: float, hl_label: str) -> Table:
    """Drop-to-liq at one leverage across Null LLTVs vs an HL-style reference."""
    header = [
        Paragraph("LLTV / regime", styles["th"]),
        Paragraph("Open LTV", styles["th"]),
        Paragraph("Drop to liq.", styles["th"]),
        Paragraph("vs HL (pp)", styles["th"]),
        Paragraph("Openable?", styles["th"]),
    ]
    hl_drop = drop_to_liq(leverage, hl_ref_lltv)
    ol = open_ltv(leverage)
    rows = [header]

    regimes = [
        ("Null 91.5% (current)", NULL_CURRENT_LLTV, True),
        ("Null 93%", 0.93, False),
        ("Null 95%", 0.95, False),
        (hl_label, hl_ref_lltv, False),
        ("Null 97%", 0.97, False),
        ("Null 97.5% (≡ HL 20×-max)", HL_EFF_LLTV_20, False),
        ("Null 99%", 0.99, False),
        ("Null 100% (zero equity)", 1.00, False),
    ]

    # Deduplicate if hl_ref already matches a Null row label target
    seen_lltvs: set[float] = set()
    emphasize = {1}  # current Null row

    for label, lltv, _em in regimes:
        key = round(lltv, 6)
        # Keep HL ref even if same number as a Null candidate; skip true duplicates of Null rows only
        if key in seen_lltvs and not label.startswith("HL"):
            continue
        seen_lltvs.add(key)

        d = drop_to_liq(leverage, lltv)
        openable = ol < lltv
        if not openable:
            cell = styles["td_warn"]
            drop_str = "impossible"
            delta_str = "—"
            open_str = "No (open ≥ LLTV)"
        else:
            cell = styles["td_em"] if label.startswith("Null 91.5%") else styles["td"]
            drop_str = fmt_pct(d, 1)
            if label.startswith("HL"):
                delta_str = "0.0 (ref)"
            elif d is None or hl_drop is None:
                delta_str = "—"
            else:
                delta_str = f"{(d - hl_drop) * 100:+.1f}"
            open_str = "Yes"

        if label.startswith("HL"):
            cell = styles["td"]

        rows.append(
            [
                Paragraph(label, cell),
                Paragraph(fmt_pct(ol, 2), cell),
                Paragraph(drop_str, cell),
                Paragraph(delta_str, cell),
                Paragraph(open_str, cell),
            ]
        )

    col_w = [2.35 * inch, 0.85 * inch, 0.95 * inch, 0.85 * inch, 1.15 * inch]
    return styled_table(rows, col_w, emphasize_rows={1})


def leverage_summary_table(styles) -> Table:
    """One row per focus leverage: drops at key LLTVs + min LLTV + match-HL LLTVs."""
    header = [
        Paragraph("Lev", styles["th"]),
        Paragraph("Open LTV", styles["th"]),
        Paragraph("Drop @91.5%", styles["th"]),
        Paragraph("Drop @95%", styles["th"]),
        Paragraph("Drop @97%", styles["th"]),
        Paragraph("Drop @99%", styles["th"]),
        Paragraph("Drop @100%", styles["th"]),
        Paragraph("Min LLTV to open", styles["th"]),
        Paragraph("LLTV ≡ HL 10×-max", styles["th"]),
        Paragraph("LLTV ≡ HL 20×-max", styles["th"]),
        Paragraph("LLTV ≡ HL 50×-max", styles["th"]),
    ]
    rows = [header]
    for L in FOCUS_LEVERAGES:
        ol = open_ltv(L)
        min_ll = min_lltv_to_open(L)
        cell = styles["td"]
        rows.append(
            [
                Paragraph(fmt_lev(L, 0), styles["td_em"]),
                Paragraph(fmt_pct(ol, 2), cell),
                Paragraph(fmt_pct(drop_to_liq(L, 0.915), 1), cell),
                Paragraph(fmt_pct(drop_to_liq(L, 0.95), 1), cell),
                Paragraph(fmt_pct(drop_to_liq(L, 0.97), 1), cell),
                Paragraph(fmt_pct(drop_to_liq(L, 0.99), 1), cell),
                Paragraph(fmt_pct(drop_to_liq(L, 1.00), 1), cell),
                Paragraph(f">{fmt_pct(min_ll, 2)}", styles["td_em"]),
                Paragraph(fmt_pct(HL_EFF_LLTV_10, 1), cell),
                Paragraph(fmt_pct(HL_EFF_LLTV_20, 2), cell),
                Paragraph(fmt_pct(HL_EFF_LLTV_50, 1), cell),
            ]
        )
    col_w = [
        0.45 * inch,
        0.65 * inch,
        0.7 * inch,
        0.65 * inch,
        0.65 * inch,
        0.65 * inch,
        0.7 * inch,
        0.85 * inch,
        0.85 * inch,
        0.85 * inch,
        0.85 * inch,
    ]
    return styled_table(rows, col_w)


def lltv_vs_max_lev_table(styles) -> Table:
    header = [
        Paragraph("LLTV", styles["th"]),
        Paragraph("Max leverage (= 1/(1−LLTV))", styles["th"]),
        Paragraph("Open LTV at that max", styles["th"]),
        Paragraph("Notes", styles["th"]),
    ]
    rows = [header]
    entries = [
        (0.915, "Current Null"),
        (0.93, "Modest raise"),
        (0.95, "Match HL 10×-max mm; unlocks 20×"),
        (0.97, "Between HL 10× and 20× mm"),
        (0.975, "Match HL 20×-max mm"),
        (0.98, "Unlocks 50×"),
        (0.99, "Match HL 50×-max mm"),
        (0.995, "Very thin oracle buffer"),
        (1.00, "Zero-equity / naive 1/L bankruptcy"),
    ]
    for lltv, note in entries:
        ml = max_leverage(lltv)
        ol_at_max = None if ml is None else open_ltv(ml)
        # At exactly LLTV = open LTV, cushion is zero; max is approached from below
        note_p = note
        if lltv >= 1.0:
            note_p = note
            ol_str = "→ 100%"
            ml_str = "unbounded (formula)"
        else:
            ml_str = fmt_lev(ml, 2)
            ol_str = fmt_pct(ol_at_max, 2) if ol_at_max is not None else "—"
            if abs(lltv - 0.95) < 1e-9:
                note_p = "≥95% needed for 20×"
            elif abs(lltv - 0.98) < 1e-9:
                note_p = "≥98% needed for 50×"
        cell = styles["td_em"] if lltv in (0.95, 0.98) else styles["td"]
        rows.append(
            [
                Paragraph(fmt_pct(lltv, 1 if lltv not in (0.975, 0.995) else 2), cell),
                Paragraph(ml_str, cell),
                Paragraph(ol_str, cell),
                Paragraph(note_p, cell),
            ]
        )
    col_w = [0.9 * inch, 2.0 * inch, 1.5 * inch, 2.6 * inch]
    return styled_table(rows, col_w, emphasize_rows={4, 7})  # 95% and 98% rows (1-indexed data)


def target_lltv_table(styles) -> Table:
    """LLTV needed so drop equals a chosen target (match HL mm or leave a cushion)."""
    header = [
        Paragraph("Leverage L", styles["th"]),
        Paragraph("Target: match HL 10×-max drop", styles["th"]),
        Paragraph("Target: match HL 20×-max drop", styles["th"]),
        Paragraph("Target: match HL 50×-max drop", styles["th"]),
        Paragraph("Target: leave 5% cushion", styles["th"]),
        Paragraph("Target: leave 2% cushion", styles["th"]),
        Paragraph("Naive 1/L (LLTV)", styles["th"]),
    ]
    rows = [header]
    for L in [5.0, 10.0, 20.0, 50.0]:
        # Drop under each HL-style regime at this L
        d10 = drop_to_liq(L, HL_EFF_LLTV_10)
        d20 = drop_to_liq(L, HL_EFF_LLTV_20)
        d50 = drop_to_liq(L, HL_EFF_LLTV_50)

        def cell_for(target_drop: float | None) -> str:
            if target_drop is None:
                return "—"
            need = lltv_to_match_drop(L, target_drop)
            # Also need LLTV > open LTV
            floor = min_lltv_to_open(L)
            if need is None:
                return "—"
            if need <= floor:
                # Matching that drop would require LLTV ≤ open LTV (impossible / already tighter)
                return f"{fmt_pct(need, 2)}*"
            return fmt_pct(need, 2)

        rows.append(
            [
                Paragraph(fmt_lev(L, 0), styles["td_em"]),
                Paragraph(cell_for(d10), styles["td"]),
                Paragraph(cell_for(d20), styles["td"]),
                Paragraph(cell_for(d50), styles["td"]),
                Paragraph(cell_for(0.05), styles["td"]),
                Paragraph(cell_for(0.02), styles["td"]),
                Paragraph("100%", styles["td"]),
            ]
        )
    col_w = [
        0.7 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
        1.1 * inch,
        1.1 * inch,
        0.9 * inch,
    ]
    return styled_table(rows, col_w)


def build_pdf() -> None:
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="Null liquidation vs Hyperliquid-style mm",
        author="Null",
    )

    story = []
    story.append(
        Paragraph("Null liquidation vs Hyperliquid-style maintenance margin", styles["title"])
    )
    story.append(
        Paragraph(
            "How much the market can move against a position before liquidation, from 5× through "
            "50×. Morpho-loop Null vs Hyperliquid-style mm = 1/(2M) for a venue max leverage M. "
            "Includes the LLTV needed to unlock 20× and 50×.",
            styles["subtitle"],
        )
    )

    # --- Theory ---
    story.append(Paragraph("1. Theory", styles["h1"]))

    story.append(
        Paragraph(
            "<b>What a perpetual futures contract does.</b> A perp lets you hold a leveraged "
            "long or short without owning the asset. You post margin (collateral). "
            "<i>Maintenance margin</i> (mm) is the minimum equity you must keep as a share of "
            "position size. Liquidation fires when equity falls to that floor, "
            "<b>not</b> when equity hits zero. On many venues, for a market with max leverage "
            "<b>M</b>, maintenance margin is set near <b>mm = 1/(2M)</b>. That is 5% for 10×-max "
            "alts, 2.5% for 20×-max, and 1% for 50×-max. The residual cushion between starting "
            "equity and wipeout shrinks as M rises.",
            styles["body"],
        )
    )

    story.append(
        Paragraph(
            "<b>What Null does.</b> Null’s looped exposure is a Morpho-style borrow loop, not a "
            "classic perp clearinghouse. You deposit collateral and borrow against it repeatedly "
            "until leverage matches the target. The position opens at "
            "<b>LTV = 1 − 1/leverage</b> "
            "(LTV = loan-to-value: debt ÷ collateral value). Examples: 5× → 80% LTV; 10× → 90%; "
            "20× → 95%; 50× → 98%. Morpho liquidates when LTV reaches <b>LLTV</b> "
            "(liquidation LTV: the hard ceiling). Today’s Null LLTV is about <b>91.5%</b>.",
            styles["body"],
        )
    )

    story.append(
        Paragraph(
            "As the collateral price falls, debt stays fixed in dollar terms while collateral "
            "value shrinks, so LTV rises. The drop that takes you from open LTV to LLTV is:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "drop_to_liq = 1 − (open_LTV / LLTV) = 1 − (1 − 1/L) / LLTV",
            styles["formula"],
        )
    )

    story.append(
        Paragraph(
            "<b>Openability constraint.</b> You cannot open at full open LTV = 1 − 1/L unless "
            "<b>LLTV &gt; 1 − 1/L</b>. At 20×, open LTV = 95%, so LLTV must be strictly above 95%. "
            "At 50×, open LTV = 98%, so LLTV must be strictly above 98%. At today’s 91.5% LLTV, "
            "anything whose open LTV ≥ 91.5% (roughly L ≥ 1/(1−0.915) ≈ 11.8×) is impossible "
            "at full open LTV. Those rows show as “impossible” in the tables.",
            styles["body"],
        )
    )

    story.append(
        Paragraph(
            "<b>Mapping HL mm → effective LLTV.</b> Set LLTV_eff = 1 − mm. Then:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "10×-max: mm 5% → LLTV_eff 95% &nbsp;|&nbsp; "
            "20×-max: mm 2.5% → LLTV_eff 97.5% &nbsp;|&nbsp; "
            "50×-max: mm 1% → LLTV_eff 99%",
            styles["formula"],
        )
    )
    story.append(
        Paragraph(
            "This puts both systems on one chart. It does not mean Morpho and HL liquidate "
            "identically (oracles, fees, partial fills differ). It does mean the first-order "
            "price cushion is comparable once you fix leverage. Matching naive bankruptcy "
            "(drop = 1/L, zero residual equity) requires LLTV = 100%.",
            styles["body"],
        )
    )

    story.append(
        Paragraph(
            "<b>Worked 5× example (unchanged intuition).</b> At 5× with LLTV 91.5%: open LTV = 80%, "
            f"drop ≈ <b>{fmt_pct(drop_to_liq(5, 0.915))}</b>. "
            f"With LLTV 95% (HL 10×-max mm): drop ≈ <b>{fmt_pct(drop_to_liq(5, 0.95))}</b>. "
            "The gap is the LLTV gap, not a mystery about leverage labels.",
            styles["body"],
        )
    )

    # --- What LLTV for 20x / 50x ---
    story.append(Paragraph("2. What LLTV do we need for 20× / 50×?", styles["h1"]))
    story.append(
        Paragraph(
            "Theoretical max leverage at full open LTV is the inverse of the leftover equity "
            "above LLTV:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "max_leverage = 1 / (1 − LLTV) &nbsp;&nbsp;⇒&nbsp;&nbsp; "
            "LLTV ≥ 1 − 1/L to unlock leverage L",
            styles["formula"],
        )
    )
    story.append(
        Paragraph(
            f"• <b>For 20×:</b> need LLTV ≥ <b>95%</b> "
            f"(exactly 95% gives max_lev = {fmt_lev(max_leverage(0.95))}; practically LLTV must be "
            f"<i>strictly above</i> 95% so open LTV 95% still has a non-zero cushion). "
            f"At LLTV 95.5%, drop at 20× ≈ {fmt_pct(drop_to_liq(20, 0.955), 2)}.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            f"• <b>For 50×:</b> need LLTV ≥ <b>98%</b> "
            f"(max_lev at 98% = {fmt_lev(max_leverage(0.98))}). "
            f"Strictly above 98% for a positive cushion. "
            f"At LLTV 98.5%, drop at 50× ≈ {fmt_pct(drop_to_liq(50, 0.985), 2)}.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            f"• <b>To match HL-style residual</b> (mm = 1/(2M) mapped as LLTV = 1 − mm): "
            f"use <b>97.5%</b> to match a 20×-max venue’s mm, or <b>99%</b> to match a 50×-max "
            f"venue’s mm. Those are higher than the bare unlock thresholds (95% / 98%) because "
            f"HL keeps a maintenance cushion; bare unlock only gets open LTV under the ceiling.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Current 91.5%:</b> theoretical max ≈ "
            f"<b>{fmt_lev(max_leverage(0.915), 2)}</b>. "
            "20× and 50× cannot open at full open LTV today.",
            styles["bullet"],
        )
    )

    story.append(Paragraph("<b>LLTV vs theoretical max leverage</b>", styles["h2"]))
    story.append(lltv_vs_max_lev_table(styles))
    story.append(
        Paragraph(
            "Table: at LLTV = open LTV the cushion is zero, so usable max leverage is approached "
            "from below the formula value. Highlighted rows: 95% unlocks 20×; 98% unlocks 50×.",
            styles["note"],
        )
    )

    # --- Summary matrix ---
    story.append(Paragraph("3. Drop matrix across leverages", styles["h1"]))
    story.append(
        Paragraph(
            "For each leverage of interest: open LTV, drop at candidate Null LLTVs, minimum LLTV "
            "to open (strictly greater than open LTV), and the HL-style effective LLTVs for "
            "10× / 20× / 50×-max venues. “—” means open LTV ≥ that LLTV (impossible).",
            styles["body"],
        )
    )
    story.append(leverage_summary_table(styles))
    story.append(
        Paragraph(
            "Min LLTV column is the open-LTV floor (need LLTV &gt; that value). "
            "HL columns are the venue-mapped LLTV_eff = 1 − 1/(2M), independent of your L: "
            "they are the LLTV that reproduces that venue’s residual margin rule.",
            styles["note"],
        )
    )

    # --- Per-leverage comparison tables ---
    story.append(Paragraph("4. Per-leverage comparison tables", styles["h1"]))
    story.append(
        Paragraph(
            "Adverse price move (%) before liquidation. Negative “vs HL” means Null liquidates "
            "sooner (tighter). Positive means more cushion than the stated HL-style reference. "
            "Reference for 5×/10× tables: HL 10×-max (mm 5%). For 20×/25×: HL 20×-max (mm 2.5%). "
            "For 40×/50×: HL 50×-max (mm 1%).",
            styles["note"],
        )
    )

    detail_specs = [
        (5.0, HL_EFF_LLTV_10, "HL 10×-max mm 5% (≡ LLTV 95%)"),
        (10.0, HL_EFF_LLTV_10, "HL 10×-max mm 5% (≡ LLTV 95%)"),
        (20.0, HL_EFF_LLTV_20, "HL 20×-max mm 2.5% (≡ LLTV 97.5%)"),
        (25.0, HL_EFF_LLTV_20, "HL 20×-max mm 2.5% (≡ LLTV 97.5%)"),
        (40.0, HL_EFF_LLTV_50, "HL 50×-max mm 1% (≡ LLTV 99%)"),
        (50.0, HL_EFF_LLTV_50, "HL 50×-max mm 1% (≡ LLTV 99%)"),
    ]

    for i, (L, hl_lltv, hl_label) in enumerate(detail_specs):
        ol = open_ltv(L)
        story.append(
            Paragraph(
                f"<b>At {fmt_lev(L, 0)} leverage</b> (open LTV = {fmt_pct(ol, 2)})",
                styles["body"],
            )
        )
        story.append(comparison_table(L, styles, hl_lltv, hl_label))
        d_cur = drop_to_liq(L, NULL_CURRENT_LLTV)
        if d_cur is None:
            story.append(
                Paragraph(
                    f"At {fmt_lev(L, 0)} with current LLTV 91.5%, open LTV ({fmt_pct(ol, 2)}) "
                    f"already meets or exceeds the ceiling. This leverage cannot open at full "
                    f"open LTV today. Raise LLTV above {fmt_pct(ol, 2)} first.",
                    styles["note"],
                )
            )
        else:
            story.append(
                Paragraph(
                    f"Current Null cushion ≈ {fmt_pct(d_cur)}; "
                    f"HL-style ref cushion ≈ {fmt_pct(drop_to_liq(L, hl_lltv))}.",
                    styles["note"],
                )
            )
        if i == 2:
            story.append(PageBreak())

    # --- Target LLTV ---
    story.append(Paragraph("5. LLTV needed to hit a target drop", styles["h1"]))
    story.append(
        Paragraph(
            "Solve for LLTV given a desired cushion: "
            "LLTV = open_LTV / (1 − target_drop). "
            "Columns show the LLTV that makes Null’s drop equal the HL-style drop at that L "
            "(for 10× / 20× / 50×-max mm), or equal a fixed 5% / 2% cushion. "
            "Naive 1/L bankruptcy is always LLTV = 100%. "
            "An asterisk means the solved LLTV is at or below open LTV (not usable).",
            styles["body"],
        )
    )
    story.append(target_lltv_table(styles))
    story.append(
        Paragraph(
            "To leave a 5% cushion at 20×: LLTV = 0.95 / 0.95 = 100%. "
            "At high leverage, even a modest absolute cushion forces LLTV near 100%.",
            styles["note"],
        )
    )

    # --- Chart ---
    story.append(Paragraph("6. Chart: liquidation drop % vs leverage", styles["h1"]))
    story.append(
        Paragraph(
            "Solid curves are Null LLTVs. Dashed / dash-dot / dotted lines are HL-style "
            "references for 10×-max (95%), 20×-max (97.5%), and 50×-max (99%). "
            "Markers annotate the current Null (91.5%) curve at 5×, 10×, 20×, and 50× "
            "(20× and 50× have no marker on 91.5% because those points are impossible).",
            styles["body"],
        )
    )
    img = Image(str(CHART_PATH), width=7.1 * inch, height=4.2 * inch)
    story.append(img)
    story.append(
        Paragraph(
            "Figure: price drop to liquidation (%) vs leverage (2×–55×) for Null LLTV curves "
            "and HL-style mm references.",
            styles["caption"],
        )
    )

    # --- What we could do ---
    story.append(Paragraph("7. What we could do", styles["h1"]))

    story.append(
        Paragraph(
            "• <b>Unlock 20×: raise LLTV to ≥95% (practically a bit above).</b> "
            "Bare unlock at 95%; matching HL 20×-max residual wants ~97.5%. "
            "Requires Morpho market risk review: higher LLTV means less buffer for oracles "
            "and bad debt.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Unlock 50×: raise LLTV to ≥98% (practically a bit above).</b> "
            "Matching HL 50×-max residual wants ~99%. At these levels the Morpho liquidation "
            "bonus and oracle latency dominate risk; the formula cushion is tiny.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Match HL 10×-alt feel without going higher: LLTV 95%.</b> "
            f"Same first-order cushion as mm 5% at every L "
            f"(~{fmt_pct(drop_to_liq(5, 0.95))} at 5×, ~{fmt_pct(drop_to_liq(10, 0.95))} at 10×). "
            "Also the minimum to open 20×.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Target 99–100% for naive-perp-like feel.</b> LLTV 100% liquidates only when "
            f"equity is gone in the loop sense (drop = 1/L). LLTV 99% is almost as loose and "
            "matches HL 50×-max mm. True perps still use mm &gt; 0; 100% is the mathematical "
            "zero-equity limit.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Middle steps: 93% or 97%.</b> 93% narrows the gap to HL 10×-max without "
            "unlocking 20×. 97% overshoots HL 10×-max, sits near HL 20×-max (97.5%), and "
            "unlocks up to ~33×.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Open with headroom.</b> Keep LLTV fixed but open below max LTV for the chosen "
            "leverage (or cap advertised leverage below what the loop can reach). That widens "
            "the drop-to-liq without a Morpho parameter change, at the cost of less capital "
            "efficiency for the user.",
            styles["bullet"],
        )
    )
    story.append(
        Paragraph(
            "• <b>UX-only display caveats.</b> If product keeps 91.5% LLTV, show “adverse move to "
            "liquidation” next to leverage, and avoid implying HL-style mm cushions. Display "
            "changes do not change risk; they only set expectations. Cap advertised max "
            f"leverage near {fmt_lev(max_leverage(0.915), 1)} until LLTV rises.",
            styles["bullet"],
        )
    )

    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Formulas assume isolated price moves on collateral, constant debt, and no "
            "funding/interest. Real liquidations also depend on oracle latency, liquidation "
            "bonuses, and partial close mechanics.",
            styles["note"],
        )
    )

    doc.build(story)


def main() -> None:
    build_chart()
    build_pdf()
    if OLD_PDF_PATH.exists() and OLD_PDF_PATH != PDF_PATH:
        OLD_PDF_PATH.unlink()
        print(f"Removed old PDF: {OLD_PDF_PATH.name}")
    print(f"Chart: {CHART_PATH}")
    print(f"PDF:   {PDF_PATH}")

    # Sanity checks
    d5_915 = drop_to_liq(5, 0.915)
    d5_95 = drop_to_liq(5, 0.95)
    assert d5_915 is not None and abs(d5_915 - 0.126) < 0.002, d5_915
    assert d5_95 is not None and abs(d5_95 - 0.158) < 0.002, d5_95
    assert drop_to_liq(20, 0.915) is None
    assert drop_to_liq(50, 0.915) is None
    assert abs(max_leverage(0.95) - 20.0) < 1e-9
    assert abs(max_leverage(0.98) - 50.0) < 1e-9
    assert abs(HL_EFF_LLTV_20 - 0.975) < 1e-12
    assert abs(HL_EFF_LLTV_50 - 0.99) < 1e-12
    assert abs(min_lltv_to_open(20) - 0.95) < 1e-12
    assert abs(min_lltv_to_open(50) - 0.98) < 1e-12

    print(f"Sanity 5× @91.5%: {fmt_pct(d5_915)} | 5× @95%: {fmt_pct(d5_95)}")
    print(f"20× needs LLTV ≥ {fmt_pct(min_lltv_to_open(20))} | max@95% = {fmt_lev(max_leverage(0.95))}")
    print(f"50× needs LLTV ≥ {fmt_pct(min_lltv_to_open(50))} | max@98% = {fmt_lev(max_leverage(0.98))}")
    print(
        f"HL-style LLTV_eff: 10×-max {fmt_pct(HL_EFF_LLTV_10)} | "
        f"20×-max {fmt_pct(HL_EFF_LLTV_20, 2)} | 50×-max {fmt_pct(HL_EFF_LLTV_50)}"
    )


if __name__ == "__main__":
    main()
