"""Cost-benefit analysis section."""

from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.sections.base import BaseSection

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class CostSection(BaseSection):
    """Renders the cost-benefit analysis section."""

    def _cost_table(self) -> list[Flowable]:
        st = self.styles.get_styles()

        # Cost items are string-based, pulled from the strings dict
        cost_items: list[dict[str, str]] = []
        for i in range(1, 7):
            item = self._s(f"cost_item_{i}")
            value = self._s(f"cost_value_{i}")
            if item:
                cost_items.append({"item": item, "value": value})

        header = [
            self._s("cost_col_item"),
            self._s("cost_col_detail"),
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
            Paragraph(self._s("cost_benefits_title"), st["SubSection"]),
        ]
        for i in range(1, 7):
            text = self._s(f"cost_benefit_{i}")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 8))
        return elements

    def _roi(self) -> list[Flowable]:
        st = self.styles.get_styles()
        roi_text = self._s("cost_roi_body")
        if not roi_text:
            return []
        return [
            Paragraph(self._s("cost_roi_title"), st["SubSection"]),
            Paragraph(roi_text, st["BodyText2"]),
            Spacer(1, 8),
        ]

    # ── Public API ───────────────────────────────────────────────

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self._s("cost_title"), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self._s("cost_body"), st["BodyText2"])
        )

        elements.extend(self._cost_table())
        elements.extend(self._benefits())
        elements.extend(self._roi())

        elements.append(PageBreak())
        return elements
