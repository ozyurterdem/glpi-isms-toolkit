"""PDF report sections."""

from glpi_toolkit.reports.pdf.sections.base import BaseSection
from glpi_toolkit.reports.pdf.sections.conclusion import ConclusionSection
from glpi_toolkit.reports.pdf.sections.configurations import ConfigurationsSection
from glpi_toolkit.reports.pdf.sections.cost import CostSection
from glpi_toolkit.reports.pdf.sections.cover import CoverSection
from glpi_toolkit.reports.pdf.sections.executive import ExecutiveSection
from glpi_toolkit.reports.pdf.sections.isms import ISMSSection
from glpi_toolkit.reports.pdf.sections.iso27001 import ISO27001Section

__all__ = [
    "BaseSection",
    "ConclusionSection",
    "ConfigurationsSection",
    "CostSection",
    "CoverSection",
    "ExecutiveSection",
    "ISMSSection",
    "ISO27001Section",
]
