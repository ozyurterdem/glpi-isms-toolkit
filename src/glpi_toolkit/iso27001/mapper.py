"""ISO 27001:2022 Control Mapper — maps GLPI configurations to Annex A controls.

Reads the ``iso27001.yml`` configuration file produced by the user and compares
it against the full 93-control Annex A database to calculate coverage, identify
gaps, and generate a text-based gap analysis report.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from glpi_toolkit.iso27001.controls import (
    CATEGORY_LABELS,
    CATEGORY_TOTALS,
    get_all_controls,
    get_controls_by_category,
)


class ISO27001Mapper:
    """Maps user-provided GLPI control statuses to the ISO 27001:2022 Annex A framework.

    Args:
        config: The parsed ``iso27001.yml`` configuration dict.  Expected keys:
            - ``controls``: list of dicts with at least ``id`` and ``status``.
            - ``totals`` (optional): informational, not used for calculation.
    """

    VALID_STATUSES = {"covered", "partial", "uncovered"}

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._user_controls: dict[str, dict[str, Any]] = {}
        self._parse_config()

    # ── Private helpers ────────────────────────────────────────────────────

    def _parse_config(self) -> None:
        """Index user-supplied control entries by control ID."""
        for entry in self._config.get("controls", []):
            control_id: str = entry.get("id", "")
            if control_id:
                self._user_controls[control_id] = entry

    def _status_for(self, control_id: str) -> str:
        """Return the status for a control, defaulting to 'uncovered'."""
        entry = self._user_controls.get(control_id)
        if entry is None:
            return "uncovered"
        status = entry.get("status", "uncovered")
        return status if status in self.VALID_STATUSES else "uncovered"

    def _enrich(self, control: dict[str, str]) -> dict[str, Any]:
        """Merge the base control dict with user-provided mapping data."""
        control_id = control["id"]
        user = self._user_controls.get(control_id, {})
        return {
            **control,
            "status": self._status_for(control_id),
            "glpi_mapping": user.get("glpi_mapping", ""),
            "isms_ref": user.get("isms_ref", ""),
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
        lines: list[str] = []
        summary = self.get_coverage_summary()
        overall = self.get_overall_percentage()
        covered_list = self.get_covered_controls()
        partial_list = self.get_partial_controls()
        uncovered_list = self.get_uncovered_controls()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # ── Header ────────────────────────────────────────────────────────
        lines.append("=" * 72)
        lines.append("  ISO 27001:2022 — Gap Analysis Report")
        lines.append(f"  Generated: {now}")
        lines.append("=" * 72)
        lines.append("")

        # ── Overall Summary ───────────────────────────────────────────────
        lines.append("OVERALL COVERAGE")
        lines.append("-" * 40)
        lines.append(f"  Total controls:     93")
        lines.append(f"  Covered:            {len(covered_list)}")
        lines.append(f"  Partially covered:  {len(partial_list)}")
        lines.append(f"  Uncovered:          {len(uncovered_list)}")
        lines.append(f"  Coverage:           {overall}%")
        lines.append("")

        # ── Per-Category Breakdown ────────────────────────────────────────
        lines.append("COVERAGE BY CATEGORY")
        lines.append("-" * 72)
        header = f"  {'Category':<40} {'Total':>5} {'Cov':>5} {'Part':>5} {'Gap':>5} {'%':>6}"
        lines.append(header)
        lines.append("  " + "-" * 68)

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

        # ── Uncovered Controls Detail ─────────────────────────────────────
        if uncovered_list:
            lines.append("UNCOVERED CONTROLS (require implementation)")
            lines.append("-" * 72)
            current_cat = ""
            for ctrl in uncovered_list:
                cat_label = CATEGORY_LABELS.get(ctrl["category"], ctrl["category"])
                if cat_label != current_cat:
                    current_cat = cat_label
                    lines.append(f"\n  [{current_cat}]")
                lines.append(f"    {ctrl['id']:<8} {ctrl['name']}")
            lines.append("")

        # ── Partially Covered Controls ────────────────────────────────────
        if partial_list:
            lines.append("PARTIALLY COVERED CONTROLS (need improvement)")
            lines.append("-" * 72)
            for ctrl in partial_list:
                mapping = ctrl.get("glpi_mapping", "—")
                lines.append(f"  {ctrl['id']:<8} {ctrl['name']}")
                lines.append(f"           Current mapping: {mapping}")
            lines.append("")

        # ── Covered Controls ──────────────────────────────────────────────
        if covered_list:
            lines.append("COVERED CONTROLS")
            lines.append("-" * 72)
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

        # ── Recommendations ───────────────────────────────────────────────
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 72)

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
        for category, cat_data in summary.items():
            if cat_data["uncovered"] > 0:
                lines.append(
                    f"  - {cat_data['label']}: {cat_data['uncovered']} gaps remaining "
                    f"({cat_data['percentage']}% covered)"
                )

        lines.append("")
        lines.append("=" * 72)
        lines.append("  End of Gap Analysis Report")
        lines.append("=" * 72)

        return "\n".join(lines)
