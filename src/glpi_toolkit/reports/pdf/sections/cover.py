"""Cover page section — title, subtitle, metadata, and branding band."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from glpi_toolkit.reports.pdf.styles import ReportStyles

PAGE_WIDTH, PAGE_HEIGHT = A4


class _ColorBand(Flowable):
    """Full-width colored rectangle used as cover background."""

    def __init__(self, width: float, height: float, color: Any) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self._color = color

    def draw(self) -> None:
        self.canv.setFillColor(self._color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


class CoverSection:
    """Renders the report cover page."""

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
        """Return flowables for the cover page."""
        company = self.config.get("company", {})
        report = company.get("report", {})
        c = self.styles.colors
        st = self.styles.get_styles()

        company_name = company.get("name", "")
        version = report.get("version", "1.0")
        date_fmt = report.get("date_format", "%B %d, %Y")
        date_str = datetime.now().strftime(date_fmt)
        confidentiality = company.get("confidentiality", "")

        elements: list[Flowable] = []

        # Background band
        elements.append(_ColorBand(PAGE_WIDTH, 320, c.primary))
        elements.append(Spacer(1, 40))

        # Title and subtitle
        elements.append(Paragraph(self.s.get("cover_title", ""), st["CoverTitle"]))
        elements.append(Spacer(1, 8))
        elements.append(
            Paragraph(self.s.get("cover_subtitle", ""), st["CoverSubtitle"])
        )
        elements.append(Spacer(1, 24))

        # Metadata table
        meta_data = [
            [self.s.get("cover_company", ""), company_name],
            [self.s.get("cover_version", ""), f"v{version}"],
            [self.s.get("cover_date", ""), date_str],
            [self.s.get("cover_classification", ""), confidentiality],
        ]
        meta_table = Table(meta_data, colWidths=[120, 300])
        meta_table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (0, 0), (0, -1), c.white),
                    ("TEXTCOLOR", (1, 0), (1, -1), c.white),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("LEFTPADDING", (1, 0), (1, -1), 12),
                ]
            )
        )
        elements.append(meta_table)
        elements.append(PageBreak())
        return elements
