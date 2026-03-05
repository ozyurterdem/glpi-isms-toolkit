"""ISO 27001 compliance section — control table, category summary, roadmap."""

from __future__ import annotations

from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.styles import ReportStyles

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class ISO27001Section:
    """Renders the ISO 27001 compliance overview."""

    def __init__(
        self,
        config: dict[str, Any],
        styles: ReportStyles,
        strings: dict[str, str],
    ) -> None:
        self.config = config
        self.styles = styles
        self.s = strings

    def _control_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        controls: list[dict[str, Any]] = self.config.get("controls", [])

        header = [
            self.s.get("iso_ctrl_id", ""),
            self.s.get("iso_ctrl_name", ""),
            self.s.get("iso_ctrl_mapping", ""),
            self.s.get("iso_ctrl_status", ""),
        ]
        rows: list[list[str]] = [header]
        for ctrl in controls:
            status_raw = ctrl.get("status", "")
            status_label = self.s.get(f"iso_status_{status_raw}", status_raw)
            rows.append([
                ctrl.get("id", ""),
                ctrl.get("name", ""),
                ctrl.get("glpi_mapping", ""),
                status_label,
            ])

        return [
            Paragraph(self.s.get("iso_controls_title", ""), st["SubSection"]),
            Paragraph(self.s.get("iso_controls_body", ""), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.10, USABLE * 0.22, USABLE * 0.50, USABLE * 0.18],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _category_summary(self) -> list[Flowable]:
        st = self.styles.get_styles()
        totals: dict[str, Any] = self.config.get("totals", {})

        header = [
            self.s.get("iso_cat_name", ""),
            self.s.get("iso_cat_total", ""),
            self.s.get("iso_cat_covered", ""),
            self.s.get("iso_cat_partial", ""),
            self.s.get("iso_cat_coverage", ""),
        ]
        rows: list[list[str]] = [header]

        for cat_key in ("organizational", "people", "physical", "technological"):
            cat = totals.get(cat_key, {})
            total = cat.get("total", 0)
            covered = cat.get("covered", 0)
            partial = cat.get("partial", 0)
            pct = f"{int(covered / total * 100)}%" if total else "0%"
            cat_label = self.s.get(f"iso_cat_{cat_key}", cat_key.title())
            rows.append([cat_label, str(total), str(covered), str(partial), pct])

        # Grand total row
        grand = totals.get("grand_total", {})
        g_total = grand.get("total", 0)
        g_covered = grand.get("covered", 0)
        g_partial = grand.get("partial", 0)
        g_pct = f"{int(g_covered / g_total * 100)}%" if g_total else "0%"
        rows.append([
            self.s.get("iso_cat_grand_total", ""),
            str(g_total),
            str(g_covered),
            str(g_partial),
            g_pct,
        ])

        return [
            Paragraph(self.s.get("iso_summary_title", ""), st["SubSection"]),
            make_table(
                rows,
                [USABLE * 0.25, USABLE * 0.15, USABLE * 0.20, USABLE * 0.20, USABLE * 0.20],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _roadmap(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = [
            Paragraph(self.s.get("iso_roadmap_title", ""), st["SubSection"]),
            Paragraph(self.s.get("iso_roadmap_body", ""), st["BodyText2"]),
        ]
        for key in ("iso_roadmap_1", "iso_roadmap_2", "iso_roadmap_3", "iso_roadmap_4"):
            text = self.s.get(key, "")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 8))
        return elements

    # ── Public API ───────────────────────────────────────────────

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self.s.get("iso_title", ""), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self.s.get("iso_body", ""), st["BodyText2"])
        )

        elements.extend(self._control_table())
        elements.extend(self._category_summary())
        elements.extend(self._roadmap())

        elements.append(PageBreak())
        return elements
