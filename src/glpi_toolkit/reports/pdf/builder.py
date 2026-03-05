"""PDFReportBuilder — orchestrates section rendering into a single PDF."""

from __future__ import annotations

from datetime import datetime
from functools import partial
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Flowable

from glpi_toolkit.core.config import ToolkitConfig
from glpi_toolkit.reports.pdf.components import header_footer
from glpi_toolkit.reports.pdf.styles import ReportStyles
from glpi_toolkit.reports.pdf.sections.cover import CoverSection
from glpi_toolkit.reports.pdf.sections.executive import ExecutiveSection
from glpi_toolkit.reports.pdf.sections.configurations import ConfigurationsSection
from glpi_toolkit.reports.pdf.sections.isms import ISMSSection
from glpi_toolkit.reports.pdf.sections.iso27001 import ISO27001Section
from glpi_toolkit.reports.pdf.sections.cost import CostSection
from glpi_toolkit.reports.pdf.sections.conclusion import ConclusionSection

PAGE_WIDTH, PAGE_HEIGHT = A4


class PDFReportBuilder:
    """Builds a complete ISMS executive PDF report.

    Parameters
    ----------
    config : ToolkitConfig
        Validated configuration from all YAML files.
    strings : dict
        Localised string map (keys referenced by each section).
    output_dir : str | Path
        Directory where the PDF will be written.
    """

    def __init__(
        self,
        config: ToolkitConfig,
        strings: dict[str, str],
        output_dir: str | Path,
    ) -> None:
        self.config = config
        self.strings = strings
        self.output_dir = Path(output_dir)

        # Resolve branding overrides from typed config
        branding = config.company.branding
        branding_dict = branding.model_dump()
        self.styles = ReportStyles(color_overrides=branding_dict)

    def _output_path(self) -> Path:
        """Generate timestamped output filename."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_short = self.config.company.short_name or "report"
        return self.output_dir / f"{company_short}_ISMS_Report_{ts}.pdf"

    def _build_doc(self, path: Path) -> BaseDocTemplate:
        """Create the ReportLab document template with header/footer."""
        doc = BaseDocTemplate(
            str(path),
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=50,
            bottomMargin=50,
        )

        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            PAGE_WIDTH - doc.leftMargin - doc.rightMargin,
            PAGE_HEIGHT - doc.topMargin - doc.bottomMargin,
            id="main",
        )

        company_name = self.config.company.name
        confidentiality = self.config.company.confidentiality
        report_title = self.strings.get("cover_title", "")

        on_page = partial(
            header_footer,
            company_name=company_name,
            confidentiality=confidentiality,
            report_title=report_title,
            accent_color=self.styles.colors.accent,
        )

        # Cover page has no header/footer
        cover_frame = Frame(0, 0, PAGE_WIDTH, PAGE_HEIGHT, id="cover")
        doc.addPageTemplates(
            [
                PageTemplate(id="Cover", frames=[cover_frame]),
                PageTemplate(id="Content", frames=[frame], onPage=on_page),
            ]
        )
        return doc

    def _collect_flowables(self) -> list[Flowable]:
        """Instantiate every section and collect their flowables."""
        args = (self.config, self.styles, self.strings)

        sections = [
            CoverSection(*args),
            ExecutiveSection(*args),
            ConfigurationsSection(*args),
            ISMSSection(*args),
            ISO27001Section(*args),
            CostSection(*args),
            ConclusionSection(*args),
        ]

        flowables: list[Flowable] = []
        for i, section in enumerate(sections):
            rendered = section.render()
            flowables.extend(rendered)
            # After cover, switch to Content template
            if i == 0 and rendered:
                from reportlab.platypus import NextPageTemplate

                flowables.insert(len(flowables) - 1, NextPageTemplate("Content"))

        return flowables

    def build(self) -> str:
        """Generate the PDF and return the output file path."""
        path = self._output_path()
        doc = self._build_doc(path)
        flowables = self._collect_flowables()
        doc.build(flowables)
        return str(path)
