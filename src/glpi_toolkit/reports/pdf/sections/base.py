"""Abstract base class for PDF report sections."""

from __future__ import annotations

from abc import ABC, abstractmethod

from reportlab.platypus import Flowable

from glpi_toolkit.core.config import ToolkitConfig
from glpi_toolkit.reports.pdf.styles import ReportStyles


class BaseSection(ABC):
    """Base class all report sections must inherit from."""

    def __init__(
        self,
        config: ToolkitConfig,
        styles: ReportStyles,
        strings: dict[str, str],
    ) -> None:
        self.config = config
        self.styles = styles
        self.strings = strings

    @abstractmethod
    def render(self) -> list[Flowable]:
        """Return flowables for this section."""
        ...

    def _s(self, key: str, default: str = "") -> str:
        """Shortcut for string lookup."""
        return self.strings.get(key, default)
