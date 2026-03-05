"""PPTX presentation generation."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from glpi_toolkit.core.config import load_config
from glpi_toolkit.reports.pptx.builder import PresentationBuilder

__all__ = ["PresentationBuilder", "generate_pptx"]


def generate_pptx(
    config_dir: Path,
    output_path: Path,
    language: str = "en",
) -> str:
    """High-level helper: load config + strings and build a PPTX.

    Parameters
    ----------
    config_dir:
        Directory containing ``company.yml``, ``sla.yml``, etc.
    output_path:
        Full path (including filename) for the output ``.pptx``.
        The parent directory will be used as the builder output dir.
    language:
        Language code for the strings file (default ``"en"``).

    Returns
    -------
    str
        Absolute path to the generated ``.pptx`` file.
    """
    config = load_config(config_dir)

    # Resolve templates/ from config_dir parent (project root)
    project_root = config_dir.resolve().parent
    strings_file = project_root / "templates" / f"strings_{language}.yml"
    if not strings_file.is_file():
        strings_file = project_root / "templates" / "strings_en.yml"
    if not strings_file.is_file():
        # Fallback: try the package-relative path
        pkg_root = Path(__file__).resolve().parent.parent.parent.parent
        strings_file = pkg_root / "templates" / f"strings_{language}.yml"
        if not strings_file.is_file():
            strings_file = pkg_root / "templates" / "strings_en.yml"

    strings: dict[str, Any] = {}
    if strings_file.is_file():
        with open(strings_file, encoding="utf-8") as f:
            strings = yaml.safe_load(f) or {}

    builder = PresentationBuilder(config, strings, output_path.parent)
    return builder.build()
