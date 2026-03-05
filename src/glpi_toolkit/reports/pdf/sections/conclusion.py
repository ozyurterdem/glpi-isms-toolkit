"""Conclusion and next-steps section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Flowable, Paragraph, Spacer

from glpi_toolkit.reports.pdf.styles import ReportStyles


class ConclusionSection:
    """Renders the conclusion and recommended next steps."""

    def __init__(
        self,
        config: dict[str, Any],
        styles: ReportStyles,
        strings: dict[str, str],
    ) -> None:
        self.config = config
        self.styles = styles
        self.s = strings

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        # Section heading
        elements.append(
            Paragraph(self.s.get("conclusion_title", ""), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))

        # Summary paragraph
        elements.append(
            Paragraph(self.s.get("conclusion_body", ""), st["BodyText2"])
        )
        elements.append(Spacer(1, 10))

        # Key achievements
        elements.append(
            Paragraph(self.s.get("conclusion_achievements_title", ""), st["SubSection"])
        )
        for i in range(1, 7):
            text = self.s.get(f"conclusion_achievement_{i}", "")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 10))

        # Recommended next steps
        elements.append(
            Paragraph(self.s.get("conclusion_next_title", ""), st["SubSection"])
        )
        for i in range(1, 9):
            text = self.s.get(f"conclusion_next_{i}", "")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 10))

        # Closing statement
        closing = self.s.get("conclusion_closing", "")
        if closing:
            elements.append(Paragraph(closing, st["BodyText2"]))

        return elements
