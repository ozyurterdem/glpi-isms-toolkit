"""PresentationBuilder — assembles a 16:9 PPTX from config + strings.

Usage::

    builder = PresentationBuilder(config=cfg, strings=strings, output_dir="/tmp")
    path = builder.build()
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Emu

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


class PresentationBuilder:
    """Build a branded executive PPTX presentation.

    Parameters
    ----------
    config : dict
        Merged configuration (company.yml + sla.yml + iso27001.yml etc.)
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
        config: dict[str, Any],
        strings: dict[str, Any],
        output_dir: str | Path,
    ) -> None:
        self._cfg = config
        self._s = strings
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Resolve theme from branding section
        branding: dict[str, str] = (
            self._cfg.get("company", {}).get("branding") or {}
        )
        self._theme = SlideTheme.from_config(branding)
        self._font = self._theme.font_family

        self._prs = Presentation()
        self._prs.slide_width = _SLIDE_WIDTH
        self._prs.slide_height = _SLIDE_HEIGHT

    # ── public API ────────────────────────────────────────────────────────

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

        company_short = self._cfg.get("company", {}).get("short_name", "Report")
        filename = f"{company_short}_Executive_Report.pptx"
        out_path = self._output_dir / filename
        self._prs.save(str(out_path))
        return str(out_path)

    # ── helpers ───────────────────────────────────────────────────────────

    def _new_slide(self) -> Any:
        """Append a blank slide and apply the dark background."""
        layout = self._prs.slide_layouts[6]  # blank layout
        slide = self._prs.slides.add_slide(layout)
        set_slide_bg(slide, self._theme.bg_dark)
        return slide

    def _company(self, key: str, default: str = "") -> str:
        return str(self._cfg.get("company", {}).get(key, default))

    def _str(self, section: str, key: str, default: str = "") -> str:
        return str(self._s.get(section, {}).get(key, default))

    def _str_list(self, section: str, key: str) -> list[str]:
        val = self._s.get(section, {}).get(key, [])
        if isinstance(val, list):
            return [str(v) for v in val]
        return []

    # ── Slide 1: Cover ────────────────────────────────────────────────────

    def _slide_cover(self) -> None:
        slide = self._new_slide()
        t = self._theme

        # Accent bar at top
        bar = slide.shapes.add_shape(1, Cm(0), Cm(0), _SLIDE_WIDTH, Cm(0.4))
        bar.fill.solid()
        bar.fill.fore_color.rgb = t.accent
        bar.line.fill.background()

        # Company name
        add_text_box(
            slide, 3.0, 4.0, 28.0, 2.5,
            text=self._company("name", "Company"),
            font_size=18, color=t.text_secondary, bold=False,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Main title
        add_text_box(
            slide, 3.0, 6.0, 28.0, 3.0,
            text=self._str("cover", "title", "Executive IT Report"),
            font_size=40, color=t.text_primary, bold=True,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Subtitle
        add_text_box(
            slide, 3.0, 9.5, 28.0, 2.0,
            text=self._str("cover", "subtitle", ""),
            font_size=18, color=t.text_secondary, bold=False,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Date
        date_fmt = (
            self._cfg.get("company", {}).get("report", {}).get("date_format")
            or "%B %d, %Y"
        )
        add_text_box(
            slide, 3.0, 12.0, 28.0, 1.0,
            text=datetime.now().strftime(date_fmt),
            font_size=14, color=t.text_muted, bold=False,
            alignment=PP_ALIGN.LEFT, font_name=self._font,
        )

        # Confidentiality footer
        conf = self._company("confidentiality", "")
        if conf:
            add_text_box(
                slide, 3.0, 17.0, 28.0, 1.0,
                text=conf, font_size=10, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.LEFT, font_name=self._font,
            )

    # ── Slide 2: Agenda ───────────────────────────────────────────────────

    def _slide_agenda(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 1, self._str("agenda", "title", "Agenda"), t, self._font)

        items = self._str_list("agenda", "items")
        if items:
            add_bullet_list(
                slide, items, start_top=5.0, font_size=16,
                color=t.text_primary, left=4.0, font_name=self._font,
            )

    # ── Slide 3: KPI Overview ─────────────────────────────────────────────

    def _slide_kpi(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 2, self._str("kpi", "title", "Key Metrics"), t, self._font)

        cards: list[dict[str, Any]] = self._s.get("kpi", {}).get("cards", [])
        kpi_colors = [t.kpi_blue, t.kpi_green, t.kpi_orange, t.kpi_red]

        left_start = 2.0
        card_width = 6.8
        gap = 0.8

        for idx, card_data in enumerate(cards[:4]):
            card_left = left_start + idx * (card_width + gap)
            add_kpi_card(
                slide,
                left=card_left,
                top=5.5,
                value=str(card_data.get("value", "—")),
                label=str(card_data.get("label", "")),
                color=kpi_colors[idx % len(kpi_colors)],
                width=card_width,
                height=4.5,
                theme=t,
                font_name=self._font,
            )

    # ── Slide 4: SLA Summary ─────────────────────────────────────────────

    def _slide_sla(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 3, self._str("sla", "title", "SLA Summary"), t, self._font)

        # Build table from config SLA levels
        sla_cfg: dict[str, Any] = self._cfg.get("sla", {}).get("levels", {})
        header_row = self._str_list("sla", "table_headers") or [
            "Priority", "Response", "Resolution", "Examples",
        ]
        rows: list[list[str]] = [header_row]

        for _key, level in sla_cfg.items():
            name = str(level.get("name", _key))
            response = str(level.get("response", "—"))
            resolution = str(level.get("resolution", "—"))
            examples = ", ".join(level.get("examples", [])[:2])
            rows.append([name, response, resolution, examples])

        if len(rows) > 1:
            add_table(
                slide, rows,
                left=2.0, top=5.0, width=29.0,
                col_widths=[6.0, 5.0, 5.0, 13.0],
                theme=t, font_name=self._font,
            )

    # ── Slide 5: ISMS Overview ────────────────────────────────────────────

    def _slide_isms(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 4, self._str("isms", "title", "ISMS Overview"), t, self._font)

        items = self._str_list("isms", "highlights")
        if items:
            add_bullet_list(
                slide, items, start_top=5.0, font_size=15,
                color=t.text_primary, left=4.0, font_name=self._font,
            )

        # Optional sub-note
        note = self._str("isms", "note", "")
        if note:
            add_text_box(
                slide, 4.0, 14.0, 25.0, 1.5,
                text=note, font_size=12, color=t.text_muted,
                bold=False, font_name=self._font,
            )

    # ── Slide 6: ISO 27001 Coverage ───────────────────────────────────────

    def _slide_iso27001(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(
            slide, 5,
            self._str("iso27001", "title", "ISO 27001 Coverage"),
            t, self._font,
        )

        # Coverage KPI cards from totals
        totals: dict[str, Any] = self._cfg.get("totals", {})
        categories = ["organizational", "people", "physical", "technological"]
        kpi_colors = [t.kpi_blue, t.kpi_green, t.kpi_orange, t.kpi_red]

        # Localised labels
        labels: dict[str, str] = self._s.get("iso27001", {}).get("category_labels", {})

        left_start = 2.0
        card_w = 6.8
        gap = 0.8

        for idx, cat in enumerate(categories):
            cat_data = totals.get(cat, {})
            total = cat_data.get("total", 0)
            covered = cat_data.get("covered", 0)
            partial = cat_data.get("partial", 0)
            pct = round((covered + partial * 0.5) / total * 100) if total else 0

            add_kpi_card(
                slide,
                left=left_start + idx * (card_w + gap),
                top=5.5,
                value=f"{pct}%",
                label=labels.get(cat, cat.title()),
                color=kpi_colors[idx % len(kpi_colors)],
                width=card_w,
                height=4.5,
                theme=t,
                font_name=self._font,
            )

        # Grand total line
        grand = totals.get("grand_total", {})
        g_total = grand.get("total", 0)
        g_covered = grand.get("covered", 0)
        g_partial = grand.get("partial", 0)
        g_pct = round((g_covered + g_partial * 0.5) / g_total * 100) if g_total else 0

        summary_text = self._str("iso27001", "summary_template", "").format(
            covered=g_covered, partial=g_partial, total=g_total, pct=g_pct,
        ) if self._str("iso27001", "summary_template") else (
            f"{g_covered} covered + {g_partial} partial / {g_total} controls = {g_pct}%"
        )

        add_text_box(
            slide, 2.0, 11.5, 29.0, 1.5,
            text=summary_text, font_size=14, color=t.text_secondary,
            bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

    # ── Slide 7: Cost Analysis ────────────────────────────────────────────

    def _slide_cost(self) -> None:
        slide = self._new_slide()
        t = self._theme

        add_section_header(slide, 6, self._str("cost", "title", "Cost Analysis"), t, self._font)

        # Table data from strings
        table_data: list[list[str]] = self._s.get("cost", {}).get("table", [])
        if table_data:
            add_table(
                slide, table_data,
                left=2.0, top=5.0, width=29.0,
                theme=t, font_name=self._font,
            )

        note = self._str("cost", "note", "")
        if note:
            add_text_box(
                slide, 2.0, 15.0, 29.0, 1.5,
                text=note, font_size=12, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
            )

    # ── Slide 8: How-To / Quickstart ──────────────────────────────────────

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
                slide, numbered, start_top=5.0, font_size=15,
                color=t.text_primary, left=4.0, font_name=self._font,
            )

        tip = self._str("howto", "tip", "")
        if tip:
            add_text_box(
                slide, 4.0, 14.5, 25.0, 1.5,
                text=tip, font_size=12, color=t.warning,
                bold=True, font_name=self._font,
            )

    # ── Slide 9: Next Steps ───────────────────────────────────────────────

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
                slide, items, start_top=5.0, font_size=15,
                color=t.text_primary, left=4.0, font_name=self._font,
            )

        timeline = self._str("next_steps", "timeline", "")
        if timeline:
            add_text_box(
                slide, 4.0, 14.5, 25.0, 1.5,
                text=timeline, font_size=13, color=t.accent,
                bold=True, font_name=self._font,
            )

    # ── Slide 10: Closing ─────────────────────────────────────────────────

    def _slide_closing(self) -> None:
        slide = self._new_slide()
        t = self._theme

        # Accent bar
        bar = slide.shapes.add_shape(1, Cm(0), Cm(0), _SLIDE_WIDTH, Cm(0.4))
        bar.fill.solid()
        bar.fill.fore_color.rgb = t.accent
        bar.line.fill.background()

        # "Thank you" or closing headline
        add_text_box(
            slide, 3.0, 5.0, 28.0, 3.0,
            text=self._str("closing", "headline", "Thank You"),
            font_size=44, color=t.text_primary, bold=True,
            alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

        # Company name
        add_text_box(
            slide, 3.0, 9.0, 28.0, 2.0,
            text=self._company("name", ""),
            font_size=20, color=t.text_secondary, bold=False,
            alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

        # Department
        add_text_box(
            slide, 3.0, 11.5, 28.0, 1.5,
            text=self._company("department", ""),
            font_size=16, color=t.text_muted, bold=False,
            alignment=PP_ALIGN.CENTER, font_name=self._font,
        )

        # Contact / extra info
        contact = self._str("closing", "contact", "")
        if contact:
            add_text_box(
                slide, 3.0, 14.0, 28.0, 1.5,
                text=contact, font_size=14, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
            )

        # Confidentiality
        conf = self._company("confidentiality", "")
        if conf:
            add_text_box(
                slide, 3.0, 17.0, 28.0, 1.0,
                text=conf, font_size=10, color=t.text_muted,
                bold=False, alignment=PP_ALIGN.CENTER, font_name=self._font,
            )
