"""Reusable PDF components — tables, KPI cards, header/footer."""

from __future__ import annotations

from typing import Any, Sequence

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm, cm
from reportlab.platypus import Paragraph, Table, TableStyle, Flowable
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4

from glpi_toolkit.reports.pdf.styles import ReportColors, ReportStyles


PAGE_WIDTH, PAGE_HEIGHT = A4


def make_table(
    data: list[list[str | Paragraph]],
    col_widths: list[float],
    header_color: HexColor | None = None,
    report_colors: ReportColors | None = None,
) -> Table:
    """Build a styled table with alternating row colors and header styling."""
    rc = report_colors or ReportColors()
    hdr = header_color or rc.table_header

    style_commands: list[tuple[Any, ...]] = [
        ("BACKGROUND", (0, 0), (-1, 0), hdr),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, rc.border),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    # Alternating row background
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_commands.append(
                ("BACKGROUND", (0, i), (-1, i), rc.table_row_alt)
            )

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(style_commands))
    return table


def make_kpi_table(
    kpis: list[dict[str, str]],
    styles: ReportStyles,
    cols: int = 4,
) -> Table:
    """Build a grid of KPI cards.

    Each item in *kpis* must have keys ``value`` and ``label``.
    """
    s = styles.get_styles()
    cells: list[Paragraph] = []
    for kpi in kpis:
        cell_content = (
            f'<para><font size="22"><b>{kpi["value"]}</b></font><br/>'
            f'<font size="9">{kpi["label"]}</font></para>'
        )
        cells.append(Paragraph(cell_content, s["KPIValue"]))

    # Pad to fill last row
    while len(cells) % cols != 0:
        cells.append(Paragraph("", s["KPILabel"]))

    rows: list[list[Paragraph]] = []
    for i in range(0, len(cells), cols):
        rows.append(cells[i : i + cols])

    col_w = (PAGE_WIDTH - 60) / cols
    table = Table(rows, colWidths=[col_w] * cols)
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0.5, styles.colors.border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, styles.colors.border),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return table


def header_footer(
    canvas: Canvas,
    doc: Any,
    *,
    company_name: str = "",
    confidentiality: str = "",
    report_title: str = "",
    accent_color: HexColor | None = None,
) -> None:
    """Draw page header and footer on every page (called by doc.build)."""
    accent = accent_color or HexColor("#0f3460")
    canvas.saveState()

    # ── Header line ──────────────────────────────────────────────
    canvas.setStrokeColor(accent)
    canvas.setLineWidth(1)
    canvas.line(30, PAGE_HEIGHT - 40, PAGE_WIDTH - 30, PAGE_HEIGHT - 40)

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(HexColor("#7f8c8d"))
    canvas.drawString(30, PAGE_HEIGHT - 36, report_title)
    canvas.drawRightString(PAGE_WIDTH - 30, PAGE_HEIGHT - 36, company_name)

    # ── Footer ───────────────────────────────────────────────────
    canvas.setStrokeColor(accent)
    canvas.line(30, 35, PAGE_WIDTH - 30, 35)

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(HexColor("#7f8c8d"))
    canvas.drawString(30, 24, confidentiality)
    canvas.drawCentredString(PAGE_WIDTH / 2, 24, f"Page {doc.page}")
    canvas.drawRightString(PAGE_WIDTH - 30, 24, report_title)

    canvas.restoreState()
