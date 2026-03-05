"""PresentationBuilder — assembles a 16:9 PPTX from config + strings.

Usage::

    builder = PresentationBuilder(config=cfg, strings=strings, output_dir="/tmp")
    path = builder.build()
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm

from glpi_toolkit.core.config import ToolkitConfig

from .theme import SlideTheme
from .components import (
    set_slide_bg,
    add_text_box,
    add_bullet_list,
    add_table,
    add_section_header,
    add_kpi_card,
)

# Widescreen 16:9 dimensions
_SLIDE_WIDTH = Cm(33.867)
_SLIDE_HEIGHT = Cm(19.05)


class _Layout:
    """Slide layout coordinates and dimensions (centimetres)."""

    CONTENT_LEFT = 3.0
    CONTENT_TOP_TITLE = 4.0
    CONTENT_TOP_MAIN = 6.0
    CONTENT_WIDTH = 28.0
    TABLE_LEFT = 2.0
    TABLE_TOP = 5.0
    TABLE_WIDTH = 29.0
    KPI_LEFT_START = 2.0
    KPI_CARD_WIDTH = 6.8
    KPI_CARD_HEIGHT = 4.5
    KPI_GAP = 0.8
    KPI_TOP = 5.5
    BULLET_LEFT = 4.0
    BULLET_TOP = 5.0
    FOOTER_TOP = 17.0
    NOTE_TOP = 14.0
    NOTE_TOP_ALT = 14.5
    NOTE_TOP_HIGH = 15.0
    ACCENT_BAR_HEIGHT = 0.4


class PresentationBuilder:
    """Build a branded executive PPTX presentation.

    Parameters
    ----------
    config : ToolkitConfig
        Validated toolkit configuration (company, sla, iso27001, etc.).
    strings : dict
        Localised UI strings keyed by section / slide name.
        Expected top-level keys: ``cover``, ``agenda``, ``kpi``, ``sla``,
        ``isms``, ``iso27001``, ``cost``, ``howto``, ``next_steps``,
        ``closing``.
    output_dir : str | Path
        Directory where the ``.pptx`` file will be written.
    """

    def __init__(
        self,
        config: ToolkitConfig,
        strings: dict[str, Any],
        output_dir: str | Path,
    ) -> None:
        self._cfg = config
        self._s = strings
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Resolve theme from branding section
        branding = self._cfg.company.branding
        self._theme = SlideTheme.from_config(branding.model_dump())
        self._font = self._theme.font_family

        self._prs = Presentation()
        self._prs.slide_width = _SLIDE_WIDTH
        self._prs.slide_height = _SLIDE_HEIGHT

    # -- public API --------------------------------------------------------

    def build(self) -> str:
        """Generate all slides and save the file. Returns the output path."""
        self._slide_cover()
        self._slide_agenda()
        self._slide_kpi()
        self._slide_sla()
        self._slide_isms()
        self._slide_iso27001()
        self._slide_cost()
        self._slide_howto()
        self._slide_next_steps()
        self._slide_closing()

        company_short = self._cfg.company.short_name or "Report"
        filename = f"{company_short}_Executive_Report.pptx"
        out_path = self._output_dir / filename
        self._prs.save(str(out_path))
        return str(out_path)

    # -- helpers -----------------------------------------------------------

    def _new_slide(self) -> Any:
        """Append a blank slide and apply the dark background."""
        layout = self._prs.slide_layouts[6]  # blank layout
        slide = self._prs.slides.add_slide(layout)
        set_slide_bg(slide, self._theme.bg_dark)
        return slide

    def _company(self, key: str, default: str = "") -> str:
        return str(getattr(self._cfg.company, key, default))

    def _str(self, section: str, key: str, default: str = "") -> str:
        return str(self._s.get(section, {}).get(key, default))

    def _str_list(self, section: str, key: str) -> list[str]:
        val = self._s.get(section, {}).get(key, [])
        if isinstance(val, list):
            return [str(v) for v in val]
        return []

    # -- Slide 1: Cover ----------------------------------------------------

    def _slide_cover(self) -> None:
        slide = self._new_slide()
        t = self._theme

        # Accent bar at top
        bar = slide.shapes.add_shape(
            1, Cm(0), Cm(0), _SLIDE_WIDTH, Cm(_Layout.ACCENT_BAR_HEIGHT),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = t.accent
        bar.line.fill.background()

        # Company name
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, _Layout.CONTENT_TOP_TITLE,
            _Layout.CONTENT_WIDTH, 2.5,
            text=self._cfg.company.name,
            font_size=18, color=t.text_secondary, bold=False,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Main title
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, _Layout.CONTENT_TOP_MAIN,
            _Layout.CONTENT_WIDTH, 3.0,
            text=self._str("cover", "title", "Executive IT Report"),
            font_size=40, color=t.text_primary, bold=True,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Subtitle
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, 9.5,
            _Layout.CONTENT_WIDTH, 2.0,
            text=self._str("cover", "subtitle", ""),
            font_size=18, color=t.text_secondary, bold=False,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Date
        date_fmt = self._cfg.company.report.date_format or "%B %d, %Y"
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, 12.0,
            _Layout.CONTENT_WIDTH, 1.0,
            text=datetime.now().strftime(date_fmt),
            font_size=14, color=t.text_muted, bold=False,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Confidentiality footer
        conf = self._cfg.company.confidentiality
        if conf:
            add_text_box(
                slide,
                _Layout.CONTENT_LEFT, _Layout.FOOTER_TOP,
                _Layout.CONTENT_WIDTH, 1.0,
                text=conf, font_size=10, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.LEFT, font_name=self._font,
            )

    # -- Slide 2: Agenda ---------------------------------------------------

    def _slide_agenda(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 1, self._str("agenda", "title", "Agenda"), t, self._font)

        items = self._str_list("agenda", "items")
        if items:
            add_bullet_list(
                slide, items,
                start_top=_Layout.BULLET_TOP, font_size=16,
                color=t.text_primary, left=_Layout.BULLET_LEFT,
                font_name=self._font,
            )

    # -- Slide 3: KPI Overview ---------------------------------------------

    def _slide_kpi(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 2, self._str("kpi", "title", "Key Metrics"), t, self._font)

        cards: list[dict[str, Any]] = self._s.get("kpi", {}).get("cards", [])
        kpi_colors = [t.kpi_blue, t.kpi_green, t.kpi_orange, t.kpi_red]

        for idx, card_data in enumerate(cards[:4]):
            card_left = _Layout.KPI_LEFT_START + idx * (_Layout.KPI_CARD_WIDTH + _Layout.KPI_GAP)
            add_kpi_card(
                slide,
                left=card_left,
                top=_Layout.KPI_TOP,
                value=str(card_data.get("value", "\u2014")),
                label=str(card_data.get("label", "")),
                color=kpi_colors[idx % len(kpi_colors)],
                width=_Layout.KPI_CARD_WIDTH,
                height=_Layout.KPI_CARD_HEIGHT,
                theme=t,
                font_name=self._font,
            )

    # -- Slide 4: SLA Summary ---------------------------------------------

    def _slide_sla(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 3, self._str("sla", "title", "SLA Summary"), t, self._font)

        # Build table from typed SLA levels
        header_row = self._str_list("sla", "table_headers") or [
            "Priority", "Response", "Resolution", "Examples",
        ]
        rows: list[list[str]] = [header_row]

        for key, level in self._cfg.sla.levels.items():
            name = level.name
            response = level.response
            resolution = level.resolution
            examples = ", ".join(level.examples[:2])
            rows.append([name, response, resolution, examples])

        if len(rows) > 1:
            add_table(
                slide, rows,
                left=_Layout.TABLE_LEFT, top=_Layout.TABLE_TOP,
                width=_Layout.TABLE_WIDTH,
                col_widths=[6.0, 5.0, 5.0, 13.0],
                theme=t, font_name=self._font,
            )

    # -- Slide 5: ISMS Overview --------------------------------------------

    def _slide_isms(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 4, self._str("isms", "title", "ISMS Overview"), t, self._font)

        items = self._str_list("isms", "highlights")
        if items:
            add_bullet_list(
                slide, items,
                start_top=_Layout.BULLET_TOP, font_size=15,
                color=t.text_primary, left=_Layout.BULLET_LEFT,
                font_name=self._font,
            )

        # Optional sub-note
        note = self._str("isms", "note", "")
        if note:
            add_text_box(
                slide,
                _Layout.BULLET_LEFT, _Layout.NOTE_TOP,
                25.0, 1.5,
                text=note, font_size=12, color=t.text_muted,
                bold=False, font_name=self._font,
            )

    # -- Slide 6: ISO 27001 Coverage ---------------------------------------

    def _slide_iso27001(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(
            slide, 5,
            self._str("iso27001", "title", "ISO 27001 Coverage"),
            t, self._font,
        )

        # Coverage KPI cards from typed totals
        totals = self._cfg.iso27001.totals
        categories = ["organizational", "people", "physical", "technological"]
        kpi_colors = [t.kpi_blue, t.kpi_green, t.kpi_orange, t.kpi_red]

        # Localised labels
        labels: dict[str, str] = self._s.get("iso27001", {}).get("category_labels", {})

        for idx, cat in enumerate(categories):
            cat_data = getattr(totals, cat)
            total = cat_data.total
            covered = cat_data.covered
            partial = cat_data.partial
            pct = round((covered + partial * 0.5) / total * 100) if total else 0

            card_left = _Layout.KPI_LEFT_START + idx * (_Layout.KPI_CARD_WIDTH + _Layout.KPI_GAP)
            add_kpi_card(
                slide,
                left=card_left,
                top=_Layout.KPI_TOP,
                value=f"{pct}%",
                label=labels.get(cat, cat.title()),
                color=kpi_colors[idx % len(kpi_colors)],
                width=_Layout.KPI_CARD_WIDTH,
                height=_Layout.KPI_CARD_HEIGHT,
                theme=t,
                font_name=self._font,
            )

        # Grand total line
        grand = self._cfg.iso27001.totals.grand_total
        g_total = grand.total
        g_covered = grand.covered
        g_partial = grand.partial
        g_pct = round((g_covered + g_partial * 0.5) / g_total * 100) if g_total else 0

        summary_text = self._str("iso27001", "summary_template", "").format(
            covered=g_covered, partial=g_partial, total=g_total, pct=g_pct,
        ) if self._str("iso27001", "summary_template") else (
            f"{g_covered} covered + {g_partial} partial / {g_total} controls = {g_pct}%"
        )

        add_text_box(
            slide,
            _Layout.TABLE_LEFT, 11.5,
            _Layout.TABLE_WIDTH, 1.5,
            text=summary_text, font_size=14, color=t.text_secondary,
            bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

    # -- Slide 7: Cost Analysis --------------------------------------------

    def _slide_cost(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 6, self._str("cost", "title", "Cost Analysis"), t, self._font)

        # Table data from strings
        table_data: list[list[str]] = self._s.get("cost", {}).get("table", [])
        if table_data:
            add_table(
                slide, table_data,
                left=_Layout.TABLE_LEFT, top=_Layout.TABLE_TOP,
                width=_Layout.TABLE_WIDTH,
                theme=t, font_name=self._font,
            )

        note = self._str("cost", "note", "")
        if note:
            add_text_box(
                slide,
                _Layout.TABLE_LEFT, _Layout.NOTE_TOP_HIGH,
                _Layout.TABLE_WIDTH, 1.5,
                text=note, font_size=12, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
            )

    # -- Slide 8: How-To / Quickstart --------------------------------------

    def _slide_howto(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(
            slide, 7,
            self._str("howto", "title", "How to Submit a Ticket"),
            t, self._font,
        )

        steps = self._str_list("howto", "steps")
        if steps:
            # Number each step
            numbered = [f"{i + 1}. {s}" for i, s in enumerate(steps)]
            add_bullet_list(
                slide, numbered,
                start_top=_Layout.BULLET_TOP, font_size=15,
                color=t.text_primary, left=_Layout.BULLET_LEFT,
                font_name=self._font,
            )

        tip = self._str("howto", "tip", "")
        if tip:
            add_text_box(
                slide,
                _Layout.BULLET_LEFT, _Layout.NOTE_TOP_ALT,
                25.0, 1.5,
                text=tip, font_size=12, color=t.warning,
                bold=True, font_name=self._font,
            )

    # -- Slide 9: Next Steps -----------------------------------------------

    def _slide_next_steps(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(
            slide, 8,
            self._str("next_steps", "title", "Next Steps"),
            t, self._font,
        )

        items = self._str_list("next_steps", "items")
        if items:
            add_bullet_list(
                slide, items,
                start_top=_Layout.BULLET_TOP, font_size=15,
                color=t.text_primary, left=_Layout.BULLET_LEFT,
                font_name=self._font,
            )

        timeline = self._str("next_steps", "timeline", "")
        if timeline:
            add_text_box(
                slide,
                _Layout.BULLET_LEFT, _Layout.NOTE_TOP_ALT,
                25.0, 1.5,
                text=timeline, font_size=13, color=t.accent,
                bold=True, font_name=self._font,
            )

    # -- Slide 10: Closing -------------------------------------------------

    def _slide_closing(self) -> None:
        slide = self._new_slide()
        t = self._theme

        # Accent bar
        bar = slide.shapes.add_shape(
            1, Cm(0), Cm(0), _SLIDE_WIDTH, Cm(_Layout.ACCENT_BAR_HEIGHT),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = t.accent
        bar.line.fill.background()

        # "Thank you" or closing headline
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, _Layout.BULLET_TOP,
            _Layout.CONTENT_WIDTH, 3.0,
            text=self._str("closing", "headline", "Thank You"),
            font_size=44, color=t.text_primary, bold=True,
            alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

        # Company name
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, 9.0,
            _Layout.CONTENT_WIDTH, 2.0,
            text=self._cfg.company.name,
            font_size=20, color=t.text_secondary, bold=False,
            alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

        # Department
        add_text_box(
            slide,
            _Layout.CONTENT_LEFT, 11.5,
            _Layout.CONTENT_WIDTH, 1.5,
            text=self._cfg.company.department,
            font_size=16, color=t.text_muted, bold=False,
            alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

        # Contact / extra info
        contact = self._str("closing", "contact", "")
        if contact:
            add_text_box(
                slide,
                _Layout.CONTENT_LEFT, _Layout.NOTE_TOP,
                _Layout.CONTENT_WIDTH, 1.5,
                text=contact, font_size=14, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
            )

        # Confidentiality
        conf = self._cfg.company.confidentiality
        if conf:
            add_text_box(
                slide,
                _Layout.CONTENT_LEFT, _Layout.FOOTER_TOP,
                _Layout.CONTENT_WIDTH, 1.0,
                text=conf, font_size=10, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
            )
