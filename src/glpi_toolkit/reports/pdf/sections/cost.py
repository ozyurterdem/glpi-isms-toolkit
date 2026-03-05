"""Cost-benefit analysis section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.styles import ReportStyles

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class CostSection:
    """Renders the cost-benefit analysis section."""

    def __init__(
        self,
        config: dict[str, Any],
        styles: ReportStyles,
        strings: dict[str, str],
    ) -> None:
        self.config = config
        self.styles = styles
        self.s = strings

    def _cost_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        cost_items: list[dict[str, str]] = self.config.get("cost_items", [])

        if not cost_items:
            # Provide generic items from strings if config has none
            cost_items = []
            for i in range(1, 7):
                item = self.s.get(f"cost_item_{i}", "")
                value = self.s.get(f"cost_value_{i}", "")
                if item:
                    cost_items.append({"item": item, "value": value})

        header = [
            self.s.get("cost_col_item", ""),
            self.s.get("cost_col_detail", ""),
        ]
        rows: list[list[str]] = [header]
        for ci in cost_items:
            rows.append([ci.get("item", ""), ci.get("value", "")])

        return [
            make_table(
                rows,
                [USABLE * 0.50, USABLE * 0.50],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _benefits(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = [
            Paragraph(self.s.get("cost_benefits_title", ""), st["SubSection"]),
        ]
        for i in range(1, 7):
            text = self.s.get(f"cost_benefit_{i}", "")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 8))
        return elements

    def _roi(self) -> list[Flowable]:
        st = self.styles.get_styles()
        roi_text = self.s.get("cost_roi_body", "")
        if not roi_text:
            return []
        return [
            Paragraph(self.s.get("cost_roi_title", ""), st["SubSection"]),
            Paragraph(roi_text, st["BodyText2"]),
            Spacer(1, 8),
        ]

    # ── Public API ───────────────────────────────────────────────

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self.s.get("cost_title", ""), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self.s.get("cost_body", ""), st["BodyText2"])
        )

        elements.extend(self._cost_table())
        elements.extend(self._benefits())
        elements.extend(self._roi())

        elements.append(PageBreak())
        return elements
