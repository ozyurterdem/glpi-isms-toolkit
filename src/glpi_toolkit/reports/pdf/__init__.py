"""PDF report generation."""

from __future__ import annotations

from pathlib import Path

import yaml

from glpi_toolkit.core.config import ToolkitConfig, load_config
from glpi_toolkit.reports.pdf.builder import PDFReportBuilder

__all__ = ["PDFReportBuilder", "generate_pdf"]


def generate_pdf(
    config_dir: Path,
    output_path: Path,
    language: str = "en",
) -> str:
    """Load configuration, resolve strings, and generate a PDF report.

    Parameters
    ----------
    config_dir:
        Path to the directory containing YAML config files.
    output_path:
        Full path (including filename) for the PDF output.
    language:
        Language code used to select the correct strings file.

    Returns
    -------
    str
        The path of the generated PDF file.
    """
    config = load_config(config_dir)

    # Resolve the templates/ directory (sibling of the config directory's parent
    # when running from the project root, or relative to the package root).
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

    strings: dict[str, str] = {}
    if strings_file.is_file():
        with open(strings_file, encoding="utf-8") as f:
            strings = yaml.safe_load(f) or {}

    builder = PDFReportBuilder(config, strings, output_path.parent)
    return builder.build()
