"""PDF report styles — color constants and ParagraphStyle definitions."""

from __future__ import annotations

from typing import Any

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


# ── Default Color Palette ────────────────────────────────────────
DEFAULT_COLORS: dict[str, str] = {
    "primary": "#1a1a2e",
    "secondary": "#16213e",
    "accent": "#0f3460",
    "highlight": "#e94560",
    "success": "#27ae60",
    "warning": "#f39c12",
    "table_header": "#1a1a2e",
    "table_row_alt": "#f8f9fa",
    "text_dark": "#2c3e50",
    "text_light": "#7f8c8d",
    "border": "#bdc3c7",
}


class ReportColors:
    """Resolved HexColor objects for use in ReportLab elements."""

    def __init__(self, overrides: dict[str, str] | None = None) -> None:
        merged = {**DEFAULT_COLORS, **(overrides or {})}
        self.primary: HexColor = HexColor(merged["primary"])
        self.secondary: HexColor = HexColor(merged["secondary"])
        self.accent: HexColor = HexColor(merged["accent"])
        self.highlight: HexColor = HexColor(merged["highlight"])
        self.success: HexColor = HexColor(merged["success"])
        self.warning: HexColor = HexColor(merged["warning"])
        self.table_header: HexColor = HexColor(merged["table_header"])
        self.table_row_alt: HexColor = HexColor(merged["table_row_alt"])
        self.text_dark: HexColor = HexColor(merged["text_dark"])
        self.text_light: HexColor = HexColor(merged["text_light"])
        self.border: HexColor = HexColor(merged["border"])
        self.white: HexColor = white  # type: ignore[assignment]


class ReportStyles:
    """Builds and holds all ParagraphStyle instances for the PDF report."""

    def __init__(self, color_overrides: dict[str, str] | None = None) -> None:
        self.colors = ReportColors(color_overrides)
        self._styles: dict[str, ParagraphStyle] = {}
        self._build()

    def _build(self) -> None:
        base = getSampleStyleSheet()
        c = self.colors

        self._styles["CoverTitle"] = ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontSize=36,
            leading=44,
            textColor=c.white,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        self._styles["CoverSubtitle"] = ParagraphStyle(
            "CoverSubtitle",
            parent=base["Title"],
            fontSize=16,
            leading=22,
            textColor=c.white,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
        self._styles["SectionTitle"] = ParagraphStyle(
            "SectionTitle",
            parent=base["Heading1"],
            fontSize=20,
            leading=26,
            textColor=c.primary,
            spaceBefore=24,
            spaceAfter=12,
            borderWidth=2,
            borderColor=c.highlight,
            borderPadding=(0, 0, 4, 0),
        )
        self._styles["SubSection"] = ParagraphStyle(
            "SubSection",
            parent=base["Heading2"],
            fontSize=14,
            leading=18,
            textColor=c.accent,
            spaceBefore=16,
            spaceAfter=8,
        )
        self._styles["BodyText2"] = ParagraphStyle(
            "BodyText2",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            textColor=c.text_dark,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
        self._styles["BulletItem"] = ParagraphStyle(
            "BulletItem",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            textColor=c.text_dark,
            leftIndent=20,
            bulletIndent=10,
            spaceBefore=2,
            spaceAfter=2,
            bulletFontName="Helvetica",
            bulletFontSize=8,
        )
        self._styles["ISORef"] = ParagraphStyle(
            "ISORef",
            parent=base["BodyText"],
            fontSize=8,
            leading=10,
            textColor=c.text_light,
            alignment=TA_LEFT,
            spaceAfter=4,
        )
        self._styles["FooterText"] = ParagraphStyle(
            "FooterText",
            parent=base["Normal"],
            fontSize=7,
            leading=9,
            textColor=c.text_light,
            alignment=TA_CENTER,
        )
        self._styles["KPIValue"] = ParagraphStyle(
            "KPIValue",
            parent=base["Title"],
            fontSize=22,
            leading=28,
            textColor=c.highlight,
            alignment=TA_CENTER,
            spaceAfter=2,
        )
        self._styles["KPILabel"] = ParagraphStyle(
            "KPILabel",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=c.text_dark,
            alignment=TA_CENTER,
        )
        self._styles["TableHeader"] = ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=c.white,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )
        self._styles["TableCell"] = ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=c.text_dark,
            alignment=TA_LEFT,
        )

    def get(self, name: str) -> ParagraphStyle:
        """Return a style by name; raises KeyError if not found."""
        return self._styles[name]

    def get_styles(self) -> dict[str, ParagraphStyle]:
        """Return the full style dictionary."""
        return dict(self._styles)
