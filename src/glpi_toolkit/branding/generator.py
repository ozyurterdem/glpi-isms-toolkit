"""LogoGenerator — creates GLPI login, sidebar, icon, and favicon images.

All images are rendered via Pillow with super-sampling for crisp output.
Colour palettes come from :mod:`~glpi_toolkit.branding.themes`.

Usage::

    gen = LogoGenerator(company_name="Acme Corp", output_dir="./output")
    gen.generate_all()           # writes login.png, sidebar.png, icon.png, favicon.ico
    gen.generate_all(theme="light")
"""

from __future__ import annotations

import platform
from collections.abc import Sequence
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .themes import get_theme_colors

# ── Constants ─────────────────────────────────────────────────────────────────

SUPERSAMPLE_FACTOR: int = 10

# Cross-platform font search paths (bold / heavy preferred)
_FONT_PATHS: dict[str, list[str]] = {
    "Darwin": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ],
    "Linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ],
    "Windows": [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
    ],
}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert '#rrggbb' to an (R, G, B) tuple."""
    h = hex_str.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _hex_to_rgba(hex_str: str, alpha: int = 255) -> tuple[int, int, int, int]:
    r, g, b = _hex_to_rgb(hex_str)
    return (r, g, b, alpha)


# ── Generator ─────────────────────────────────────────────────────────────────


class LogoGenerator:
    """Generate a set of branded images for GLPI.

    Parameters
    ----------
    company_name : str
        The display name rendered in each image.
    output_dir : str | Path
        Directory where the generated images are saved.
    """

    def __init__(self, company_name: str, output_dir: str | Path) -> None:
        self._name = company_name
        self._out = Path(output_dir)
        self._out.mkdir(parents=True, exist_ok=True)

    # ── Font resolution (single helper — no duplication) ──────────────

    @staticmethod
    def _get_font(paths: Sequence[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Try each path in order; fall back to the built-in default."""
        for p in paths:
            if Path(p).is_file():
                try:
                    return ImageFont.truetype(p, size)
                except OSError:
                    continue
        # Fallback
        return ImageFont.load_default()

    def _resolve_font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Resolve a font at the requested *size* using platform-specific paths."""
        os_name = platform.system()
        paths = _FONT_PATHS.get(os_name, _FONT_PATHS["Linux"])
        return self._get_font(paths, size)

    # ── Theme helper (single source) ──────────────────────────────────

    @staticmethod
    def _get_theme_colors(theme: str = "dark") -> dict[str, str]:
        """Return resolved theme colour dict."""
        return get_theme_colors(theme)

    # ── Chrome / 3-D text helper ──────────────────────────────────────

    @staticmethod
    def _draw_chrome_text(
        draw: ImageDraw.ImageDraw,
        xy: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        highlight: tuple[int, int, int, int],
        shadow: tuple[int, int, int, int],
        offset: int = 2,
    ) -> None:
        """Draw text with a shadow + highlight to give a chrome / 3-D effect.

        *shadow* is rendered below-right, *highlight* is the main fill.
        """
        sx, sy = xy
        # Shadow layer
        draw.text((sx + offset, sy + offset), text, font=font, fill=shadow)
        # Main text
        draw.text((sx, sy), text, font=font, fill=highlight)

    # ── Image builders ────────────────────────────────────────────────

    def _make_login_logo(self, colors: dict[str, str]) -> Image.Image:
        """Login page logo — wide banner with company name."""
        final_w, final_h = 800, 200
        ss = SUPERSAMPLE_FACTOR
        w, h = final_w * ss, final_h * ss

        img = Image.new("RGBA", (w, h), _hex_to_rgba(colors["bg"], 0))
        draw = ImageDraw.Draw(img)
        font = self._resolve_font(int(72 * ss))

        # Centered text with chrome effect
        bbox = draw.textbbox((0, 0), self._name, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (w - tw) // 2
        ty = (h - th) // 2

        self._draw_chrome_text(
            draw, (tx, ty), self._name, font,
            highlight=_hex_to_rgba(colors["accent"]),
            shadow=_hex_to_rgba(colors["shadow"], 120),
            offset=3 * ss,
        )

        return img.resize((final_w, final_h), Image.LANCZOS)

    def _make_sidebar_logo(self, colors: dict[str, str]) -> Image.Image:
        """Sidebar logo — compact horizontal lockup."""
        final_w, final_h = 250, 50
        ss = SUPERSAMPLE_FACTOR
        w, h = final_w * ss, final_h * ss

        img = Image.new("RGBA", (w, h), _hex_to_rgba(colors["bg"], 0))
        draw = ImageDraw.Draw(img)
        font = self._resolve_font(int(28 * ss))

        bbox = draw.textbbox((0, 0), self._name, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (w - tw) // 2
        ty = (h - th) // 2

        self._draw_chrome_text(
            draw, (tx, ty), self._name, font,
            highlight=_hex_to_rgba(colors["fg"]),
            shadow=_hex_to_rgba(colors["shadow"], 80),
            offset=2 * ss,
        )

        return img.resize((final_w, final_h), Image.LANCZOS)

    def _make_icon(self, colors: dict[str, str]) -> Image.Image:
        """Square icon with the first letter on a coloured circle."""
        final_size = 256
        ss = SUPERSAMPLE_FACTOR
        size = final_size * ss

        img = Image.new("RGBA", (size, size), _hex_to_rgba(colors["icon_bg"]))
        draw = ImageDraw.Draw(img)

        # Circle
        margin = size // 10
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=_hex_to_rgba(colors["highlight"]),
        )

        # Letter
        letter = self._name[0].upper() if self._name else "?"
        font = self._resolve_font(int(140 * ss))
        bbox = draw.textbbox((0, 0), letter, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (size - tw) // 2
        ty = (size - th) // 2 - bbox[1]  # compensate for top bearing

        self._draw_chrome_text(
            draw, (tx, ty), letter, font,
            highlight=_hex_to_rgba(colors["icon_fg"]),
            shadow=_hex_to_rgba(colors["shadow"], 100),
            offset=4 * ss,
        )

        return img.resize((final_size, final_size), Image.LANCZOS)

    def _make_favicon(self, colors: dict[str, str]) -> Image.Image:
        """16x16 / 32x32 multi-size favicon source (returned as 64px RGBA)."""
        final_size = 64
        ss = SUPERSAMPLE_FACTOR
        size = final_size * ss

        img = Image.new("RGBA", (size, size), _hex_to_rgba(colors["favicon_bg"]))
        draw = ImageDraw.Draw(img)

        # Rounded rectangle background
        margin = size // 8
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=size // 5,
            fill=_hex_to_rgba(colors["highlight"]),
        )

        letter = self._name[0].upper() if self._name else "?"
        font = self._resolve_font(int(36 * ss))
        bbox = draw.textbbox((0, 0), letter, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (size - tw) // 2
        ty = (size - th) // 2 - bbox[1]

        draw.text((tx, ty), letter, font=font, fill=_hex_to_rgba(colors["favicon_fg"]))

        return img.resize((final_size, final_size), Image.LANCZOS)

    # ── Public API ────────────────────────────────────────────────────

    def generate_all(self, theme: str = "dark") -> dict[str, Path]:
        """Generate all branding assets and return a map of name to file path.

        Parameters
        ----------
        theme : str
            One of ``"dark"``, ``"light"``, ``"grey"``.

        Returns
        -------
        dict[str, Path]
            Keys: ``login``, ``sidebar``, ``icon``, ``favicon``.
        """
        colors = self._get_theme_colors(theme)

        outputs: dict[str, Path] = {}

        # Login logo
        login_img = self._make_login_logo(colors)
        login_path = self._out / "login.png"
        login_img.save(str(login_path), "PNG")
        outputs["login"] = login_path

        # Sidebar logo
        sidebar_img = self._make_sidebar_logo(colors)
        sidebar_path = self._out / "sidebar.png"
        sidebar_img.save(str(sidebar_path), "PNG")
        outputs["sidebar"] = sidebar_path

        # Icon
        icon_img = self._make_icon(colors)
        icon_path = self._out / "icon.png"
        icon_img.save(str(icon_path), "PNG")
        outputs["icon"] = icon_path

        # Favicon (.ico with multiple sizes)
        favicon_src = self._make_favicon(colors)
        favicon_path = self._out / "favicon.ico"
        # Create multi-resolution ICO
        sizes = [(16, 16), (32, 32), (48, 48)]
        ico_images = [favicon_src.resize(s, Image.LANCZOS) for s in sizes]
        ico_images[0].save(
            str(favicon_path), format="ICO",
            sizes=[(s.width, s.height) for s in ico_images],
            append_images=ico_images[1:],
        )
        outputs["favicon"] = favicon_path

        return outputs
