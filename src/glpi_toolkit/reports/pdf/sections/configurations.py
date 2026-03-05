"""System configurations section — locations, categories, SLA, templates, rules."""

from __future__ import annotations

from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.styles import ReportStyles

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class ConfigurationsSection:
    """Renders the system configuration details section."""

    def __init__(
        self,
        config: dict[str, Any],
        styles: ReportStyles,
        strings: dict[str, str],
    ) -> None:
        self.config = config
        self.styles = styles
        self.s = strings

    # ── Sub-renderers ────────────────────────────────────────────

    def _locations_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        locations: list[dict[str, Any]] = self.config.get("locations", [])
        header = [self.s.get("cfg_zone", ""), self.s.get("cfg_rooms", "")]
        rows: list[list[str]] = [header]
        for loc in locations:
            zone = loc.get("zone", "")
            rooms = ", ".join(loc.get("rooms", []))
            rows.append([zone, rooms])

        return [
            Paragraph(self.s.get("cfg_locations_title", ""), st["SubSection"]),
            Paragraph(self.s.get("cfg_locations_body", ""), st["BodyText2"]),
            make_table(rows, [USABLE * 0.25, USABLE * 0.75], report_colors=self.styles.colors),
            Spacer(1, 12),
        ]

    def _categories_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        categories: list[dict[str, Any]] = self.config.get("categories", [])
        header = [
            self.s.get("cfg_category", ""),
            self.s.get("cfg_type", ""),
            self.s.get("cfg_subcategories", ""),
        ]
        rows: list[list[str]] = [header]
        for cat in categories:
            subs = ", ".join(
                s.get("name", "") for s in cat.get("subcategories", [])
            )
            rows.append([cat.get("name", ""), cat.get("type", ""), subs])

        return [
            Paragraph(self.s.get("cfg_categories_title", ""), st["SubSection"]),
            Paragraph(self.s.get("cfg_categories_body", ""), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.2, USABLE * 0.12, USABLE * 0.68],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _sla_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        sla_cfg = self.config.get("sla", {})
        levels: dict[str, Any] = sla_cfg.get("levels", {})
        header = [
            self.s.get("cfg_sla_level", ""),
            self.s.get("cfg_sla_response", ""),
            self.s.get("cfg_sla_resolution", ""),
            self.s.get("cfg_sla_examples", ""),
        ]
        rows: list[list[str]] = [header]
        for _key, level in levels.items():
            examples = ", ".join(level.get("examples", [])[:2])
            rows.append([
                level.get("name", ""),
                level.get("response", ""),
                level.get("resolution", ""),
                examples,
            ])

        return [
            Paragraph(self.s.get("cfg_sla_title", ""), st["SubSection"]),
            Paragraph(self.s.get("cfg_sla_body", ""), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.18, USABLE * 0.14, USABLE * 0.14, USABLE * 0.54],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _templates_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        templates: list[dict[str, Any]] = self.config.get("templates", [])
        header = [
            self.s.get("cfg_tpl_name", ""),
            self.s.get("cfg_tpl_type", ""),
            self.s.get("cfg_tpl_priority", ""),
            self.s.get("cfg_tpl_group", ""),
        ]
        rows: list[list[str]] = [header]
        for tpl in templates:
            rows.append([
                tpl.get("name", ""),
                tpl.get("type", ""),
                tpl.get("priority", ""),
                tpl.get("assigned_group", ""),
            ])

        return [
            Paragraph(self.s.get("cfg_templates_title", ""), st["SubSection"]),
            Paragraph(self.s.get("cfg_templates_body", ""), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.3, USABLE * 0.12, USABLE * 0.14, USABLE * 0.44],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _rules_table(self) -> list[Flowable]:
        st = self.styles.get_styles()
        rules: list[dict[str, Any]] = self.config.get("rules", [])
        header = [
            self.s.get("cfg_rule_name", ""),
            self.s.get("cfg_rule_condition", ""),
            self.s.get("cfg_rule_action", ""),
        ]
        rows: list[list[str]] = [header]
        for rule in rules:
            cond_parts = [
                f"{k}: {v}" for k, v in rule.get("condition", {}).items()
            ]
            act_parts = [
                f"{k}: {v}" for k, v in rule.get("action", {}).items()
            ]
            rows.append([
                rule.get("name", ""),
                "; ".join(cond_parts),
                "; ".join(act_parts),
            ])

        return [
            Paragraph(self.s.get("cfg_rules_title", ""), st["SubSection"]),
            Paragraph(self.s.get("cfg_rules_body", ""), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.35, USABLE * 0.30, USABLE * 0.35],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    # ── Public API ───────────────────────────────────────────────

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self.s.get("cfg_title", ""), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self.s.get("cfg_body", ""), st["BodyText2"])
        )

        elements.extend(self._locations_table())
        elements.extend(self._categories_table())
        elements.extend(self._sla_table())
        elements.extend(self._templates_table())
        elements.extend(self._rules_table())

        elements.append(PageBreak())
        return elements
