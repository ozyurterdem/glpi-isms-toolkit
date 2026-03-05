"""ISO 27001:2022 Control Mapper — maps GLPI configurations to Annex A controls.

Reads the ``iso27001.yml`` configuration file produced by the user and compares
it against the full 93-control Annex A database to calculate coverage, identify
gaps, and generate a text-based gap analysis report.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from glpi_toolkit.core.config import ISO27001Config, ISOControl
from glpi_toolkit.iso27001.controls import (
    CATEGORY_LABELS,
    CATEGORY_TOTALS,
    get_all_controls,
    get_controls_by_category,
)


class ISO27001Mapper:
    """Maps user-provided GLPI control statuses to the ISO 27001:2022 Annex A framework.

    Args:
        config: A validated :class:`ISO27001Config` instance containing the
            parsed ``iso27001.yml`` data with typed control entries.
    """

    VALID_STATUSES = {"covered", "partial", "uncovered"}

    def __init__(self, config: ISO27001Config) -> None:
        self._config = config
        self._user_controls: dict[str, ISOControl] = {}
        self._parse_config()

    # ── Private helpers ────────────────────────────────────────────────────

    def _parse_config(self) -> None:
        """Index user-supplied control entries by control ID."""
        for control in self._config.controls:
            if control.id:
                self._user_controls[control.id] = control

    def _status_for(self, control_id: str) -> str:
        """Return the status for a control, defaulting to 'uncovered'.

        Handles both ``"not_covered"`` (from YAML) and ``"uncovered"`` (internal).
        """
        entry = self._user_controls.get(control_id)
        if entry is None:
            return "uncovered"
        status = entry.status
        if status == "not_covered":
            return "uncovered"
        return status if status in self.VALID_STATUSES else "uncovered"

    def _enrich(self, control: dict[str, str]) -> dict[str, Any]:
        """Merge the base control dict with user-provided mapping data."""
        control_id = control["id"]
        user = self._user_controls.get(control_id)
        return {
            **control,
            "status": self._status_for(control_id),
            "glpi_mapping": user.glpi_mapping if user else "",
            "isms_ref": user.isms_ref if user else "",
        }

    def _filter_by_status(self, status: str) -> list[dict[str, Any]]:
        """Return all controls matching a given status."""
        return [
            self._enrich(c)
            for c in get_all_controls()
            if self._status_for(c["id"]) == status
        ]

    # ── Public API ─────────────────────────────────────────────────────────

    def get_covered_controls(self) -> list[dict[str, Any]]:
        """Return controls that are fully covered by GLPI configurations."""
        return self._filter_by_status("covered")

    def get_partial_controls(self) -> list[dict[str, Any]]:
        """Return controls that are only partially addressed."""
        return self._filter_by_status("partial")

    def get_uncovered_controls(self) -> list[dict[str, Any]]:
        """Return controls with no GLPI coverage."""
        return self._filter_by_status("uncovered")

    def get_coverage_summary(self) -> dict[str, dict[str, Any]]:
        """Calculate per-category coverage statistics.

        Returns:
            Dict keyed by category name, each containing::

                {
                    "label": "Organizational Controls (A.5)",
                    "total": 37,
                    "covered": 15,
                    "partial": 0,
                    "uncovered": 22,
                    "percentage": 40.5,
                }
        """
        summary: dict[str, dict[str, Any]] = {}
        for category, total in CATEGORY_TOTALS.items():
            cat_controls = get_controls_by_category(category)
            covered = sum(1 for c in cat_controls if self._status_for(c["id"]) == "covered")
            partial = sum(1 for c in cat_controls if self._status_for(c["id"]) == "partial")
            uncovered = total - covered - partial
            percentage = round((covered / total) * 100, 1) if total > 0 else 0.0

            summary[category] = {
                "label": CATEGORY_LABELS[category],
                "total": total,
                "covered": covered,
                "partial": partial,
                "uncovered": uncovered,
                "percentage": percentage,
            }
        return summary

    def get_overall_percentage(self) -> float:
        """Return the overall coverage percentage across all 93 controls.

        Only fully covered controls count towards the percentage.
        """
        total = sum(CATEGORY_TOTALS.values())
        covered = len(self.get_covered_controls())
        return round((covered / total) * 100, 1) if total > 0 else 0.0

    # ── Report rendering helpers ─────────────────────────────────────────

    def _render_header(self) -> list[str]:
        """Render the report header with generation timestamp."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return [
            "=" * 72,
            "  ISO 27001:2022 — Gap Analysis Report",
            f"  Generated: {now}",
            "=" * 72,
            "",
        ]

    def _render_overall_summary(
        self,
        covered: list[dict[str, Any]],
        partial: list[dict[str, Any]],
        uncovered: list[dict[str, Any]],
        overall: float,
    ) -> list[str]:
        """Render the overall coverage summary block."""
        return [
            "OVERALL COVERAGE",
            "-" * 40,
            "  Total controls:     93",
            f"  Covered:            {len(covered)}",
            f"  Partially covered:  {len(partial)}",
            f"  Uncovered:          {len(uncovered)}",
            f"  Coverage:           {overall}%",
            "",
        ]

    def _render_category_breakdown(self, summary: dict[str, dict[str, Any]]) -> list[str]:
        """Render the per-category coverage table."""
        lines: list[str] = [
            "COVERAGE BY CATEGORY",
            "-" * 72,
            f"  {'Category':<40} {'Total':>5} {'Cov':>5} {'Part':>5} {'Gap':>5} {'%':>6}",
            "  " + "-" * 68,
        ]
        for cat_data in summary.values():
            lines.append(
                f"  {cat_data['label']:<40} "
                f"{cat_data['total']:>5} "
                f"{cat_data['covered']:>5} "
                f"{cat_data['partial']:>5} "
                f"{cat_data['uncovered']:>5} "
                f"{cat_data['percentage']:>5.1f}%"
            )
        lines.append("")
        return lines

    def _render_uncovered_detail(self, uncovered_list: list[dict[str, Any]]) -> list[str]:
        """Render the detailed list of uncovered controls."""
        if not uncovered_list:
            return []
        lines: list[str] = [
            "UNCOVERED CONTROLS (require implementation)",
            "-" * 72,
        ]
        current_cat = ""
        for ctrl in uncovered_list:
            cat_label = CATEGORY_LABELS.get(ctrl["category"], ctrl["category"])
            if cat_label != current_cat:
                current_cat = cat_label
                lines.append(f"\n  [{current_cat}]")
            lines.append(f"    {ctrl['id']:<8} {ctrl['name']}")
        lines.append("")
        return lines

    def _render_partial_detail(self, partial_list: list[dict[str, Any]]) -> list[str]:
        """Render the detailed list of partially covered controls."""
        if not partial_list:
            return []
        lines: list[str] = [
            "PARTIALLY COVERED CONTROLS (need improvement)",
            "-" * 72,
        ]
        for ctrl in partial_list:
            mapping = ctrl.get("glpi_mapping", "\u2014")
            lines.append(f"  {ctrl['id']:<8} {ctrl['name']}")
            lines.append(f"           Current mapping: {mapping}")
        lines.append("")
        return lines

    def _render_covered_detail(self, covered_list: list[dict[str, Any]]) -> list[str]:
        """Render the detailed list of fully covered controls."""
        if not covered_list:
            return []
        lines: list[str] = [
            "COVERED CONTROLS",
            "-" * 72,
        ]
        current_cat = ""
        for ctrl in covered_list:
            cat_label = CATEGORY_LABELS.get(ctrl["category"], ctrl["category"])
            if cat_label != current_cat:
                current_cat = cat_label
                lines.append(f"\n  [{current_cat}]")
            mapping = ctrl.get("glpi_mapping", "")
            ref = ctrl.get("isms_ref", "")
            ref_str = f" ({ref})" if ref else ""
            lines.append(f"    {ctrl['id']:<8} {ctrl['name']}{ref_str}")
            if mapping:
                lines.append(f"             -> {mapping}")
        lines.append("")
        return lines

    def _render_recommendations(
        self,
        summary: dict[str, dict[str, Any]],
        overall: float,
    ) -> list[str]:
        """Render the recommendations section based on overall coverage."""
        lines: list[str] = [
            "RECOMMENDATIONS",
            "-" * 72,
        ]

        if overall < 30:
            lines.append("  [!] Coverage is LOW. Prioritize organizational and people controls")
            lines.append("      as they provide the broadest impact with least technical effort.")
        elif overall < 60:
            lines.append("  [~] Coverage is MODERATE. Focus on closing gaps in the categories")
            lines.append("      with the lowest percentages before pursuing full compliance.")
        else:
            lines.append("  [+] Coverage is GOOD. Review partially covered controls and address")
            lines.append("      remaining gaps for full ISO 27001 compliance readiness.")

        lines.append("")

        # Category-specific advice
        for cat_data in summary.values():
            if cat_data["uncovered"] > 0:
                lines.append(
                    f"  - {cat_data['label']}: {cat_data['uncovered']} gaps remaining "
                    f"({cat_data['percentage']}% covered)"
                )

        lines.append("")
        lines.append("=" * 72)
        lines.append("  End of Gap Analysis Report")
        lines.append("=" * 72)
        return lines

    # ── Public report generation ──────────────────────────────────────────

    def generate_gap_report(self) -> str:
        """Generate a text-based ISO 27001 gap analysis report.

        The report includes:
          - Header with generation timestamp
          - Per-category coverage breakdown
          - Overall summary
          - Detailed list of uncovered and partially covered controls
          - Recommendations section

        Returns:
            Multi-line string suitable for console output or file export.
        """
        summary = self.get_coverage_summary()
        overall = self.get_overall_percentage()
        covered_list = self.get_covered_controls()
        partial_list = self.get_partial_controls()
        uncovered_list = self.get_uncovered_controls()

        lines: list[str] = []
        lines.extend(self._render_header())
        lines.extend(self._render_overall_summary(covered_list, partial_list, uncovered_list, overall))
        lines.extend(self._render_category_breakdown(summary))
        lines.extend(self._render_uncovered_detail(uncovered_list))
        lines.extend(self._render_partial_detail(partial_list))
        lines.extend(self._render_covered_detail(covered_list))
        lines.extend(self._render_recommendations(summary, overall))
        return "\n".join(lines)
