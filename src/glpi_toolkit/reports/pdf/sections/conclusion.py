"""Conclusion and next-steps section."""

from __future__ import annotations

from reportlab.platypus import Flowable, Paragraph, Spacer

from glpi_toolkit.reports.pdf.sections.base import BaseSection


class ConclusionSection(BaseSection):
    """Renders the conclusion and recommended next steps."""

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        # Section heading
        elements.append(
            Paragraph(self._s("conclusion_title"), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))

        # Summary paragraph
        elements.append(
            Paragraph(self._s("conclusion_body"), st["BodyText2"])
        )
        elements.append(Spacer(1, 10))

        # Key achievements
        elements.append(
            Paragraph(self._s("conclusion_achievements_title"), st["SubSection"])
        )
        for i in range(1, 7):
            text = self._s(f"conclusion_achievement_{i}")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 10))

        # Recommended next steps
        elements.append(
            Paragraph(self._s("conclusion_next_title"), st["SubSection"])
        )
        for i in range(1, 9):
            text = self._s(f"conclusion_next_{i}")
            if text:
                elements.append(Paragraph(f"\u2022 {text}", st["BulletItem"]))
        elements.append(Spacer(1, 10))

        # Closing statement
        closing = self._s("conclusion_closing")
        if closing:
            elements.append(Paragraph(closing, st["BodyText2"]))

        return elements
