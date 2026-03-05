"""Branding colour themes for logo / asset generation.

Each theme is a dictionary of hex colour strings keyed by semantic name.
Use :func:`get_theme_colors` to retrieve a palette by name with a safe
fallback to ``"dark"``.
"""

from __future__ import annotations

from typing import Any

THEMES: dict[str, dict[str, str]] = {
    # ── Dark (default) ────────────────────────────────────────────────
    "dark": {
        "bg": "#1a1a2e",
        "bg_alt": "#16213e",
        "fg": "#ffffff",
        "fg_secondary": "#b0b0b0",
        "accent": "#e94560",
        "highlight": "#0f3460",
        "shadow": "#0d0d1a",
        "icon_bg": "#16213e",
        "icon_fg": "#e94560",
        "favicon_bg": "#1a1a2e",
        "favicon_fg": "#e94560",
    },

    # ── Light ─────────────────────────────────────────────────────────
    "light": {
        "bg": "#ffffff",
        "bg_alt": "#f4f4f8",
        "fg": "#1a1a2e",
        "fg_secondary": "#555555",
        "accent": "#e94560",
        "highlight": "#0f3460",
        "shadow": "#cccccc",
        "icon_bg": "#f4f4f8",
        "icon_fg": "#e94560",
        "favicon_bg": "#ffffff",
        "favicon_fg": "#e94560",
    },

    # ── Grey / Neutral ────────────────────────────────────────────────
    "grey": {
        "bg": "#2c2c3a",
        "bg_alt": "#3a3a4a",
        "fg": "#e0e0e0",
        "fg_secondary": "#999999",
        "accent": "#5dade2",
        "highlight": "#2e86c1",
        "shadow": "#1a1a24",
        "icon_bg": "#3a3a4a",
        "icon_fg": "#5dade2",
        "favicon_bg": "#2c2c3a",
        "favicon_fg": "#5dade2",
    },
}


def get_theme_colors(theme_name: str = "dark") -> dict[str, str]:
    """Return the colour palette for *theme_name*.

    Falls back to ``"dark"`` if the requested theme is not found.
    """
    return THEMES.get(theme_name, THEMES["dark"])
