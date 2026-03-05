"""System configurations section — locations, categories, SLA, templates, rules."""

from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.sections.base import BaseSection

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class ConfigurationsSection(BaseSection):
    """Renders the system configuration details section."""

    # ── Helpers ──────────────────────────────────────────────────

    def _table_block(
        self,
        title_key: str,
        body_key: str,
        rows: list,
        col_widths: list[float],
    ) -> list[Flowable]:
        """Build a standard sub-section: heading + description + table + spacer."""
        st = self.styles.get_styles()
        return [
            Paragraph(self._s(title_key), st["SubSection"]),
            Paragraph(self._s(body_key), st["BodyText2"]),
            make_table(rows, col_widths, report_colors=self.styles.colors),
            Spacer(1, 12),
        ]

    # ── Sub-renderers ────────────────────────────────────────────

    def _locations_table(self) -> list[Flowable]:
        locations = self.config.locations
        header = [self._s("cfg_zone"), self._s("cfg_rooms")]
        rows: list[list[str]] = [header]
        for loc in locations:
            rows.append([loc.zone, ", ".join(loc.rooms)])

        return self._table_block(
            "cfg_locations_title",
            "cfg_locations_body",
            rows,
            [USABLE * 0.25, USABLE * 0.75],
        )

    def _categories_table(self) -> list[Flowable]:
        categories = self.config.categories
        header = [
            self._s("cfg_category"),
            self._s("cfg_type"),
            self._s("cfg_subcategories"),
        ]
        rows: list[list[str]] = [header]
        for cat in categories:
            subs = ", ".join(s.name for s in cat.subcategories)
            rows.append([cat.name, cat.type, subs])

        return self._table_block(
            "cfg_categories_title",
            "cfg_categories_body",
            rows,
            [USABLE * 0.2, USABLE * 0.12, USABLE * 0.68],
        )

    def _sla_table(self) -> list[Flowable]:
        levels = self.config.sla.levels
        header = [
            self._s("cfg_sla_level"),
            self._s("cfg_sla_response"),
            self._s("cfg_sla_resolution"),
            self._s("cfg_sla_examples"),
        ]
        rows: list[list[str]] = [header]
        for _key, level in levels.items():
            examples = ", ".join(level.examples[:2])
            rows.append([
                level.name,
                level.response,
                level.resolution,
                examples,
            ])

        return self._table_block(
            "cfg_sla_title",
            "cfg_sla_body",
            rows,
            [USABLE * 0.18, USABLE * 0.14, USABLE * 0.14, USABLE * 0.54],
        )

    def _templates_table(self) -> list[Flowable]:
        templates = self.config.templates
        header = [
            self._s("cfg_tpl_name"),
            self._s("cfg_tpl_type"),
            self._s("cfg_tpl_priority"),
            self._s("cfg_tpl_group"),
        ]
        rows: list[list[str]] = [header]
        for tpl in templates:
            rows.append([
                tpl.name,
                tpl.type,
                tpl.priority,
                tpl.assigned_group,
            ])

        return self._table_block(
            "cfg_templates_title",
            "cfg_templates_body",
            rows,
            [USABLE * 0.3, USABLE * 0.12, USABLE * 0.14, USABLE * 0.44],
        )

    def _rules_table(self) -> list[Flowable]:
        rules = self.config.business_rules
        header = [
            self._s("cfg_rule_name"),
            self._s("cfg_rule_condition"),
            self._s("cfg_rule_action"),
        ]
        rows: list[list[str]] = [header]
        for rule in rules:
            cond_parts = [
                f"{k}: {v}"
                for k, v in rule.condition.model_dump(exclude_none=True).items()
            ]
            act_parts = [
                f"{k}: {v}"
                for k, v in rule.action.model_dump(exclude_none=True).items()
            ]
            rows.append([
                rule.name,
                "; ".join(cond_parts),
                "; ".join(act_parts),
            ])

        return self._table_block(
            "cfg_rules_title",
            "cfg_rules_body",
            rows,
            [USABLE * 0.35, USABLE * 0.30, USABLE * 0.35],
        )

    # ── Public API ───────────────────────────────────────────────

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self._s("cfg_title"), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self._s("cfg_body"), st["BodyText2"])
        )

        elements.extend(self._locations_table())
        elements.extend(self._categories_table())
        elements.extend(self._sla_table())
        elements.extend(self._templates_table())
        elements.extend(self._rules_table())

        elements.append(PageBreak())
        return elements
