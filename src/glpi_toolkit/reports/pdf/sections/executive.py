"""Executive summary section — overview text and KPI dashboard."""

from __future__ import annotations

from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_kpi_table
from glpi_toolkit.reports.pdf.sections.base import BaseSection


class ExecutiveSection(BaseSection):
    """Renders the executive summary with a KPI dashboard."""

    def _compute_kpis(self) -> list[dict[str, str]]:
        """Derive KPI values from config data."""
        categories = self.config.categories
        templates = self.config.templates
        controls = self.config.iso27001.controls
        profiles = self.config.security.profiles
        locations = self.config.locations

        total_categories = sum(
            len(cat.subcategories) for cat in categories
        )
        covered = sum(1 for c in controls if c.status == "covered")
        total_ctrl = len(controls)
        pct = f"{int(covered / total_ctrl * 100)}%" if total_ctrl else "0%"

        total_rooms = sum(len(loc.rooms) for loc in locations)

        return [
            {"value": str(total_categories), "label": self._s("kpi_categories")},
            {"value": str(len(templates)), "label": self._s("kpi_templates")},
            {"value": "4", "label": self._s("kpi_sla_levels")},
            {"value": pct, "label": self._s("kpi_iso_coverage")},
            {"value": str(len(profiles)), "label": self._s("kpi_rbac_roles")},
            {"value": str(total_rooms), "label": self._s("kpi_locations")},
            {"value": str(covered), "label": self._s("kpi_controls_covered")},
            {"value": str(total_ctrl), "label": self._s("kpi_controls_total")},
        ]

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self._s("exec_title"), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self._s("exec_body"), st["BodyText2"])
        )
        elements.append(Spacer(1, 12))

        # KPI dashboard
        elements.append(
            Paragraph(self._s("exec_kpi_heading"), st["SubSection"])
        )
        kpis = self._compute_kpis()
        elements.append(make_kpi_table(kpis, self.styles))
        elements.append(Spacer(1, 8))

        # Scope bullets
        elements.append(
            Paragraph(self._s("exec_scope_heading"), st["SubSection"])
        )
        for key in ("exec_scope_1", "exec_scope_2", "exec_scope_3", "exec_scope_4"):
            text = self._s(key)
            if text:
                elements.append(
                    Paragraph(f"\u2022 {text}", st["BulletItem"])
                )

        elements.append(PageBreak())
        return elements
