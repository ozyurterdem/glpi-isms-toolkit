"""Slide theme — colour palette with config-driven branding overrides."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pptx.dml.color import RGBColor
from pptx.util import Pt

__all__ = ["SlideTheme"]


def _hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert a hex colour string (e.g. '#1a1a2e') to an RGBColor."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        raise ValueError(f"Invalid hex colour: #{hex_str}")
    return RGBColor(
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16),
    )


# ── Default dark-theme palette ───────────────────────────────────────────────

_DEFAULTS: dict[str, str] = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "accent": "#e94560",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "text_muted": "#808080",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "table_header_bg": "#0f3460",
    "table_header_fg": "#ffffff",
    "table_row_alt": "#1e2a4a",
    "kpi_blue": "#3498db",
    "kpi_green": "#27ae60",
    "kpi_orange": "#f39c12",
    "kpi_red": "#e94560",
}

# Mapping from company.yml branding keys to internal theme keys
_BRANDING_MAP: dict[str, str] = {
    "primary": "bg_dark",
    "secondary": "bg_medium",
    "accent": "bg_light",
    "highlight": "accent",
    "success": "success",
    "warning": "warning",
}


@dataclass
class SlideTheme:
    """Immutable colour palette for the presentation.

    Resolved colours are exposed as ``RGBColor`` attributes.
    Pass a ``branding`` dict (hex strings keyed by the names used in
    ``company.yml``) to override the defaults.
    """

    # Backgrounds
    bg_dark: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["bg_dark"]))
    bg_medium: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["bg_medium"]))
    bg_light: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["bg_light"]))

    # Accent / highlight
    accent: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["accent"]))

    # Text
    text_primary: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["text_primary"]))
    text_secondary: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["text_secondary"]))
    text_muted: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["text_muted"]))

    # Semantic
    success: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["success"]))
    warning: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["warning"]))
    danger: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["danger"]))

    # Table
    table_header_bg: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["table_header_bg"]))
    table_header_fg: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["table_header_fg"]))
    table_row_alt: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["table_row_alt"]))

    # KPI card colours
    kpi_blue: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["kpi_blue"]))
    kpi_green: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["kpi_green"]))
    kpi_orange: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["kpi_orange"]))
    kpi_red: RGBColor = field(default_factory=lambda: _hex_to_rgb(_DEFAULTS["kpi_red"]))

    # Typography defaults (Pt)
    font_title: Pt = Pt(36)
    font_subtitle: Pt = Pt(18)
    font_heading: Pt = Pt(28)
    font_body: Pt = Pt(14)
    font_small: Pt = Pt(11)
    font_family: str = "Calibri"

    @classmethod
    def from_config(cls, branding: dict[str, str] | None = None) -> SlideTheme:
        """Create a theme, optionally overriding defaults with branding hex values."""
        overrides: dict[str, Any] = {}
        if branding:
            for brand_key, theme_key in _BRANDING_MAP.items():
                hex_val = branding.get(brand_key)
                if hex_val:
                    overrides[theme_key] = _hex_to_rgb(hex_val)
        return cls(**overrides)
