"""Reusable slide-building components for python-pptx presentations.

Every helper accepts explicit position / size values in **Cm** and
colour values as ``RGBColor`` so that callers stay in control of the
theme while this module remains stateless.
"""

from __future__ import annotations

from typing import Sequence

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.slide import Slide
from pptx.util import Cm, Pt, Emu

from .theme import SlideTheme

__all__ = [
    "set_slide_bg",
    "add_text_box",
    "add_bullet_list",
    "add_table",
    "add_section_header",
    "add_kpi_card",
]


# ── Background ────────────────────────────────────────────────────────────────


def set_slide_bg(slide: Slide, color: RGBColor) -> None:
    """Fill the entire slide background with a solid colour."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


# ── Text box ──────────────────────────────────────────────────────────────────


def add_text_box(
    slide: Slide,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    font_size: int = 14,
    color: RGBColor | None = None,
    bold: bool = False,
    alignment: PP_ALIGN = PP_ALIGN.LEFT,
    font_name: str = "Calibri",
) -> None:
    """Add a simple single-paragraph text box."""
    txbox = slide.shapes.add_textbox(Cm(left), Cm(top), Cm(width), Cm(height))
    tf = txbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = alignment
    run = p.runs[0]
    run.font.size = Pt(font_size)
    run.font.name = font_name
    run.font.bold = bold
    if color:
        run.font.color.rgb = color


# ── Bullet list ───────────────────────────────────────────────────────────────


def add_bullet_list(
    slide: Slide,
    items: Sequence[str],
    start_top: float,
    font_size: int = 14,
    color: RGBColor | None = None,
    left: float = 2.0,
    width: float = 20.0,
    line_height: float = 0.85,
    font_name: str = "Calibri",
) -> None:
    """Add a bulleted list starting at *start_top* (Cm).

    Each item occupies a separate paragraph inside a single text frame.
    """
    item_height = line_height * len(items) + 1.0
    txbox = slide.shapes.add_textbox(
        Cm(left), Cm(start_top), Cm(width), Cm(item_height)
    )
    tf = txbox.text_frame
    tf.word_wrap = True

    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.space_after = Pt(4)

        # Bullet character
        pPr = p._pPr
        if pPr is None:
            pPr = p._p.get_or_add_pPr()
        buChar = pPr.makeelement(qn("a:buChar"), {"char": "\u2022"})
        pPr.append(buChar)

        run = p.runs[0]
        run.font.size = Pt(font_size)
        run.font.name = font_name
        if color:
            run.font.color.rgb = color


# ── Table ─────────────────────────────────────────────────────────────────────


def add_table(
    slide: Slide,
    data: Sequence[Sequence[str]],
    left: float,
    top: float,
    width: float,
    col_widths: Sequence[float] | None = None,
    theme: SlideTheme | None = None,
    font_name: str = "Calibri",
    header_font_size: int = 12,
    body_font_size: int = 11,
) -> None:
    """Add a styled table with a coloured header row.

    ``data`` is a list of rows; the first row is treated as the header.
    ``col_widths`` are in Cm; if *None* columns share *width* equally.
    """
    if not data:
        return

    rows = len(data)
    cols = len(data[0])

    if col_widths is None:
        col_widths = [width / cols] * cols

    table_shape = slide.shapes.add_table(
        rows, cols, Cm(left), Cm(top), Cm(width), Cm(rows * 1.0)
    )
    table = table_shape.table

    # Column widths
    for ci, cw in enumerate(col_widths):
        table.columns[ci].width = Cm(cw)

    # Resolve theme
    t = theme or SlideTheme()

    for ri, row in enumerate(data):
        for ci, cell_text in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = str(cell_text)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

            # Style the paragraph
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.CENTER
                for run in p.runs:
                    run.font.name = font_name
                    if ri == 0:
                        run.font.size = Pt(header_font_size)
                        run.font.bold = True
                        run.font.color.rgb = t.table_header_fg
                    else:
                        run.font.size = Pt(body_font_size)
                        run.font.color.rgb = t.text_primary

            # Cell fill
            fill = cell.fill
            fill.solid()
            if ri == 0:
                fill.fore_color.rgb = t.table_header_bg
            elif ri % 2 == 0:
                fill.fore_color.rgb = t.table_row_alt
            else:
                fill.fore_color.rgb = t.bg_medium


# ── Section header ────────────────────────────────────────────────────────────


def add_section_header(
    slide: Slide,
    number: int | str,
    title: str,
    theme: SlideTheme | None = None,
    font_name: str = "Calibri",
) -> None:
    """Add a large section header with a circled number and title.

    The number badge is drawn as a bold accent-coloured text; the title
    appears right next to it.
    """
    t = theme or SlideTheme()

    # Number badge
    add_text_box(
        slide,
        left=1.5,
        top=1.0,
        width=2.5,
        height=2.0,
        text=str(number).zfill(2),
        font_size=48,
        color=t.accent,
        bold=True,
        alignment=PP_ALIGN.CENTER,
        font_name=font_name,
    )

    # Section title
    add_text_box(
        slide,
        left=4.0,
        top=1.5,
        width=20.0,
        height=1.5,
        text=title,
        font_size=32,
        color=t.text_primary,
        bold=True,
        font_name=font_name,
    )

    # Accent underline via a thin coloured rectangle
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE.RECTANGLE
        Cm(4.0),
        Cm(3.2),
        Cm(18.0),
        Cm(0.1),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = t.accent
    shape.line.fill.background()


# ── KPI card ──────────────────────────────────────────────────────────────────


def add_kpi_card(
    slide: Slide,
    left: float,
    top: float,
    value: str,
    label: str,
    color: RGBColor | None = None,
    width: float = 5.5,
    height: float = 4.0,
    theme: SlideTheme | None = None,
    font_name: str = "Calibri",
) -> None:
    """Add a KPI metric card (coloured value + label beneath)."""
    t = theme or SlideTheme()
    card_color = color or t.kpi_blue

    # Card background
    card = slide.shapes.add_shape(
        1,  # MSO_SHAPE.RECTANGLE
        Cm(left),
        Cm(top),
        Cm(width),
        Cm(height),
    )
    card.fill.solid()
    card.fill.fore_color.rgb = t.bg_medium
    card.line.fill.background()

    # Top accent strip
    strip = slide.shapes.add_shape(
        1,
        Cm(left),
        Cm(top),
        Cm(width),
        Cm(0.15),
    )
    strip.fill.solid()
    strip.fill.fore_color.rgb = card_color
    strip.line.fill.background()

    # Value text
    add_text_box(
        slide,
        left=left + 0.3,
        top=top + 0.6,
        width=width - 0.6,
        height=2.0,
        text=str(value),
        font_size=36,
        color=card_color,
        bold=True,
        alignment=PP_ALIGN.CENTER,
        font_name=font_name,
    )

    # Label text
    add_text_box(
        slide,
        left=left + 0.3,
        top=top + 2.6,
        width=width - 0.6,
        height=1.2,
        text=label,
        font_size=12,
        color=t.text_secondary,
        bold=False,
        alignment=PP_ALIGN.CENTER,
        font_name=font_name,
    )
