"""Tests for ISO 27001 module."""

from pathlib import Path

import pytest
import yaml


CONFIG_DIR = Path(__file__).parent.parent / "config"


class TestISO27001Coverage:
    """Verify ISO 27001 coverage calculations."""

    @pytest.fixture
    def controls(self) -> list[dict]:
        with open(CONFIG_DIR / "iso27001.yml") as f:
            data = yaml.safe_load(f)
        return data["controls"]

    def test_all_controls_have_category(self, controls: list[dict]) -> None:
        valid_categories = {"organizational", "people", "physical", "technological"}
        for control in controls:
            assert control.get("category") in valid_categories, (
                f"Invalid category in {control['id']}"
            )

    def test_covered_count(self, controls: list[dict]) -> None:
        covered = [c for c in controls if c["status"] == "covered"]
        assert len(covered) >= 20, f"Expected at least 20 covered controls, got {len(covered)}"

    def test_control_id_format(self, controls: list[dict]) -> None:
        import re
        pattern = re.compile(r"^A\.\d+\.\d+$")
        for control in controls:
            assert pattern.match(control["id"]), (
                f"Invalid control ID format: {control['id']}"
            )

    def test_organizational_controls(self, controls: list[dict]) -> None:
        org = [c for c in controls if c["category"] == "organizational"]
        assert all(c["id"].startswith("A.5.") for c in org)

    def test_people_controls(self, controls: list[dict]) -> None:
        people = [c for c in controls if c["category"] == "people"]
        assert all(c["id"].startswith("A.6.") for c in people)
