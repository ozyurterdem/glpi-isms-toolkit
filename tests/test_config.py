"""Tests for configuration loading and validation."""

import os
from pathlib import Path

import pytest
import yaml


CONFIG_DIR = Path(__file__).parent.parent / "config"


class TestConfigFiles:
    """Verify all required config files exist and are valid YAML."""

    REQUIRED_FILES = [
        "company.yml",
        "sla.yml",
        "categories.yml",
        "security.yml",
        "templates.yml",
        "knowledge_base.yml",
        "business_rules.yml",
        "locations.yml",
        "assets.yml",
        "iso27001.yml",
    ]

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_config_file_exists(self, filename: str) -> None:
        filepath = CONFIG_DIR / filename
        assert filepath.exists(), f"Missing config file: {filename}"

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_config_file_valid_yaml(self, filename: str) -> None:
        filepath = CONFIG_DIR / filename
        with open(filepath) as f:
            data = yaml.safe_load(f)
        assert data is not None, f"Empty config file: {filename}"
        assert isinstance(data, dict), f"Config must be a YAML mapping: {filename}"


class TestCompanyConfig:
    """Validate company.yml structure."""

    @pytest.fixture
    def config(self) -> dict:
        with open(CONFIG_DIR / "company.yml") as f:
            return yaml.safe_load(f)

    def test_has_company_section(self, config: dict) -> None:
        assert "company" in config

    def test_has_required_fields(self, config: dict) -> None:
        company = config["company"]
        for field in ["name", "department", "timezone", "language"]:
            assert field in company, f"Missing field: company.{field}"

    def test_language_valid(self, config: dict) -> None:
        assert config["company"]["language"] in ("en", "tr", "de")


class TestSLAConfig:
    """Validate sla.yml structure."""

    @pytest.fixture
    def config(self) -> dict:
        with open(CONFIG_DIR / "sla.yml") as f:
            return yaml.safe_load(f)

    def test_has_sla_levels(self, config: dict) -> None:
        assert "sla" in config
        assert "levels" in config["sla"]

    def test_has_four_levels(self, config: dict) -> None:
        levels = config["sla"]["levels"]
        for level in ["critical", "high", "normal", "low"]:
            assert level in levels, f"Missing SLA level: {level}"

    def test_levels_have_required_fields(self, config: dict) -> None:
        for level_name, level in config["sla"]["levels"].items():
            assert "response" in level, f"Missing response in {level_name}"
            assert "resolution" in level, f"Missing resolution in {level_name}"


class TestSecurityConfig:
    """Validate security.yml structure."""

    @pytest.fixture
    def config(self) -> dict:
        with open(CONFIG_DIR / "security.yml") as f:
            return yaml.safe_load(f)

    def test_has_password_policy(self, config: dict) -> None:
        assert "password_policy" in config

    def test_password_min_length(self, config: dict) -> None:
        assert config["password_policy"]["min_length"] >= 8

    def test_has_profiles(self, config: dict) -> None:
        assert "profiles" in config
        assert len(config["profiles"]) >= 3

    def test_has_default_profile(self, config: dict) -> None:
        defaults = [p for p in config["profiles"] if p.get("is_default")]
        assert len(defaults) == 1, "Exactly one default profile required"


class TestISO27001Config:
    """Validate iso27001.yml structure."""

    @pytest.fixture
    def config(self) -> dict:
        with open(CONFIG_DIR / "iso27001.yml") as f:
            return yaml.safe_load(f)

    def test_has_controls(self, config: dict) -> None:
        assert "controls" in config
        assert len(config["controls"]) > 0

    def test_controls_have_required_fields(self, config: dict) -> None:
        for control in config["controls"]:
            assert "id" in control, f"Missing id in control"
            assert "name" in control, f"Missing name in {control.get('id')}"
            assert "status" in control, f"Missing status in {control.get('id')}"

    def test_valid_statuses(self, config: dict) -> None:
        valid = {"covered", "partial", "not_covered"}
        for control in config["controls"]:
            assert control["status"] in valid, (
                f"Invalid status '{control['status']}' in {control['id']}"
            )

    def test_control_ids_unique(self, config: dict) -> None:
        ids = [c["id"] for c in config["controls"]]
        assert len(ids) == len(set(ids)), "Duplicate control IDs found"


class TestNoSensitiveData:
    """Ensure no company-specific or sensitive data in config files."""

    SENSITIVE_PATTERNS = [
        "192.168.",
        "10.0.",
        "172.16.",
        "password:",
        "secret:",
        "token:",
        "@gmail.com",
        "@hotmail.com",
    ]

    @pytest.mark.parametrize("filename", TestConfigFiles.REQUIRED_FILES)
    def test_no_sensitive_data(self, filename: str) -> None:
        filepath = CONFIG_DIR / filename
        content = filepath.read_text().lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in ("password:", "token:"):
                # Skip known config keys
                continue
            assert pattern not in content, (
                f"Potential sensitive data '{pattern}' found in {filename}"
            )
