"""Configuration loader — reads YAML files from a config directory into validated Pydantic models."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# company.yml
# ---------------------------------------------------------------------------


class ReportMeta(BaseModel):
    """Report metadata block inside company config."""

    author: str = "IT Department"
    version: str = "1.0"
    date_format: str = "%B %d, %Y"


class BrandingColors(BaseModel):
    """Hex color codes used for PDF/PPTX reports."""

    primary: str = "#1a1a2e"
    secondary: str = "#16213e"
    accent: str = "#0f3460"
    highlight: str = "#e94560"
    success: str = "#27ae60"
    warning: str = "#f39c12"

    @field_validator("*", mode="before")
    @classmethod
    def _ensure_hex(cls, v: str) -> str:
        if isinstance(v, str) and not v.startswith("#"):
            v = f"#{v}"
        return v


class CompanyConfig(BaseModel):
    """Parsed *company.yml*."""

    name: str
    short_name: str = ""
    department: str = "IT Department"
    industry: str = "manufacturing"
    timezone: str = "UTC"
    language: str = "en"
    confidentiality: str = ""

    report: ReportMeta = Field(default_factory=ReportMeta)
    branding: BrandingColors = Field(default_factory=BrandingColors)


# ---------------------------------------------------------------------------
# sla.yml
# ---------------------------------------------------------------------------


class SLALevel(BaseModel):
    """Single SLA priority level."""

    name: str
    response: str
    resolution: str
    examples: list[str] = Field(default_factory=list)


class OLAConfig(BaseModel):
    """Operational-level agreement."""

    response: str = "4h"
    resolution: str = "16h"
    description: str = ""


class CalendarHours(BaseModel):
    start: str = "08:00"
    end: str = "18:00"


class SaturdayHours(BaseModel):
    enabled: bool = False
    start: str = "08:00"
    end: str = "13:00"


class CalendarConfig(BaseModel):
    name: str = "Business Hours"
    workdays: list[str] = Field(
        default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    )
    hours: CalendarHours = Field(default_factory=CalendarHours)
    saturday: SaturdayHours = Field(default_factory=SaturdayHours)


class SLAConfig(BaseModel):
    """Parsed *sla.yml*."""

    standard: str = "itil_v4"
    levels: dict[str, SLALevel] = Field(default_factory=dict)
    ola: OLAConfig = Field(default_factory=OLAConfig)
    calendar: CalendarConfig = Field(default_factory=CalendarConfig)


# ---------------------------------------------------------------------------
# categories.yml
# ---------------------------------------------------------------------------


class SubCategory(BaseModel):
    name: str
    default_priority: str = "normal"
    group: str = ""


class CategoryConfig(BaseModel):
    """Single top-level ITIL category."""

    name: str
    type: str = "incident"
    isms_ref: str = ""
    subcategories: list[SubCategory] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# security.yml
# ---------------------------------------------------------------------------


class PasswordPolicy(BaseModel):
    isms_ref: str = ""
    min_length: int = 10
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_number: bool = True
    require_symbol: bool = True
    expiry_days: int = 90
    expiry_warning_days: int = 15
    expiry_lock_days: int = 30
    force_change_on_first_login: bool = True


class AccountLockout(BaseModel):
    isms_ref: str = ""
    max_attempts: int = 5
    lockout_minutes: int = 30


class SessionConfig(BaseModel):
    timeout_minutes: int = 30
    description: str = ""


class ProfilePermissions(BaseModel):
    tickets: str = "own"
    assets: str = "none"
    admin: bool = False


class SecurityProfile(BaseModel):
    name: str
    description: str = ""
    is_default: bool = False
    permissions: ProfilePermissions = Field(default_factory=ProfilePermissions)


class SecurityConfig(BaseModel):
    """Parsed *security.yml*."""

    password_policy: PasswordPolicy = Field(default_factory=PasswordPolicy)
    account_lockout: AccountLockout = Field(default_factory=AccountLockout)
    session: SessionConfig = Field(default_factory=SessionConfig)
    profiles: list[SecurityProfile] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# templates.yml
# ---------------------------------------------------------------------------


class TemplateConfig(BaseModel):
    """Single ticket template."""

    name: str
    category: str = ""
    priority: str = "normal"
    assigned_group: str = ""
    type: str = "incident"
    isms_ref: str = ""
    checklist: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# knowledge_base.yml
# ---------------------------------------------------------------------------


class KBArticle(BaseModel):
    title: str
    summary: str = ""
    isms_ref: str = ""


class KBCategory(BaseModel):
    name: str
    articles: list[KBArticle] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# assets.yml
# ---------------------------------------------------------------------------


class AssetState(BaseModel):
    name: str
    description: str = ""
    isms_ref: str = ""


class AssetsConfig(BaseModel):
    """Parsed *assets.yml*."""

    asset_states: list[AssetState] = Field(default_factory=list)
    computer_types: list[str] = Field(default_factory=list)
    document_categories: list[str] = Field(default_factory=list)
    software_categories: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# business_rules.yml
# ---------------------------------------------------------------------------


class RuleCondition(BaseModel, extra="allow"):
    """Flexible condition block — keys vary per rule."""

    priority: str | None = None
    category: str | list[str] | None = None
    category_parent: str | None = None


class RuleAction(BaseModel, extra="allow"):
    """Flexible action block."""

    assigned_group: str | None = None
    priority: str | None = None
    sla: str | None = None
    notify_management: bool = False


class BusinessRule(BaseModel):
    name: str
    condition: RuleCondition = Field(default_factory=RuleCondition)
    action: RuleAction = Field(default_factory=RuleAction)


# ---------------------------------------------------------------------------
# locations.yml
# ---------------------------------------------------------------------------


class LocationZone(BaseModel):
    zone: str
    rooms: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# iso27001.yml
# ---------------------------------------------------------------------------


class ISOControl(BaseModel):
    id: str
    name: str
    category: str = ""
    glpi_mapping: str = ""
    isms_ref: str = ""
    status: str = "not_covered"


class ISOCategoryTotals(BaseModel):
    total: int = 0
    covered: int = 0
    partial: int = 0


class ISOTotals(BaseModel):
    organizational: ISOCategoryTotals = Field(default_factory=ISOCategoryTotals)
    people: ISOCategoryTotals = Field(default_factory=ISOCategoryTotals)
    physical: ISOCategoryTotals = Field(default_factory=ISOCategoryTotals)
    technological: ISOCategoryTotals = Field(default_factory=ISOCategoryTotals)
    grand_total: ISOCategoryTotals = Field(default_factory=ISOCategoryTotals)


class ISO27001Config(BaseModel):
    """Parsed *iso27001.yml*."""

    controls: list[ISOControl] = Field(default_factory=list)
    totals: ISOTotals = Field(default_factory=ISOTotals)


# ---------------------------------------------------------------------------
# Root toolkit configuration
# ---------------------------------------------------------------------------


class ToolkitConfig(BaseModel):
    """Aggregated configuration from all YAML files under ``config/``."""

    company: CompanyConfig
    sla: SLAConfig = Field(default_factory=SLAConfig)
    categories: list[CategoryConfig] = Field(default_factory=list)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    templates: list[TemplateConfig] = Field(default_factory=list)
    knowledge_base: list[KBCategory] = Field(default_factory=list)
    assets: AssetsConfig = Field(default_factory=AssetsConfig)
    business_rules: list[BusinessRule] = Field(default_factory=list)
    locations: list[LocationZone] = Field(default_factory=list)
    iso27001: ISO27001Config = Field(default_factory=ISO27001Config)


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a single YAML file and return its contents as a dict."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _load_yaml_optional(path: Path) -> dict[str, Any]:
    """Load a YAML file if it exists; return empty dict otherwise."""
    if not path.is_file():
        logger.debug("Optional config not found, skipping: %s", path.name)
        return {}
    return _load_yaml(path)


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------


def _parse_list(raw: dict[str, Any], key: str, model: type[BaseModel]) -> list[Any]:
    """Parse a list of dicts from *raw[key]* into a list of *model* instances."""
    return [model(**item) for item in raw.get(key, [])]


def _parse_sla(raw: dict[str, Any]) -> SLAConfig:
    """Build an SLAConfig from raw YAML data with its nested structure."""
    sla_block = raw.get("sla", {})
    return SLAConfig(
        standard=sla_block.get("standard", "itil_v4"),
        levels={k: SLALevel(**v) for k, v in sla_block.get("levels", {}).items()},
        ola=OLAConfig(**raw["ola"]) if "ola" in raw else OLAConfig(),
        calendar=CalendarConfig(**raw["calendar"]) if "calendar" in raw else CalendarConfig(),
    )


def _parse_security(raw: dict[str, Any]) -> SecurityConfig:
    """Build a SecurityConfig from raw YAML data with its nested structure."""
    return SecurityConfig(
        password_policy=PasswordPolicy(**raw.get("password_policy", {})),
        account_lockout=AccountLockout(**raw.get("account_lockout", {})),
        session=SessionConfig(**raw.get("session", {})),
        profiles=_parse_list(raw, "profiles", SecurityProfile),
    )


def _parse_iso27001(raw: dict[str, Any]) -> ISO27001Config:
    """Build an ISO27001Config from raw YAML data with its nested structure."""
    return ISO27001Config(
        controls=_parse_list(raw, "controls", ISOControl),
        totals=ISOTotals(**raw["totals"]) if "totals" in raw else ISOTotals(),
    )


def load_config(config_dir: str | Path) -> ToolkitConfig:
    """Load and validate all configuration YAML files from *config_dir*.

    Parameters
    ----------
    config_dir:
        Path to the directory containing ``company.yml``, ``sla.yml``, etc.

    Returns
    -------
    ToolkitConfig
        Fully validated configuration object.

    Raises
    ------
    FileNotFoundError
        If *config_dir* does not exist.
    ValueError
        If the mandatory ``company.yml`` is missing.
    pydantic.ValidationError
        If any config file contains invalid data.
    """
    config_dir = Path(config_dir)
    if not config_dir.is_dir():
        raise FileNotFoundError(f"Config directory does not exist: {config_dir}")

    # -- mandatory ---------------------------------------------------------
    company_path = config_dir / "company.yml"
    if not company_path.is_file():
        raise ValueError(
            f"Mandatory config file not found: {company_path}. "
            "Copy config/examples/factory.yml to config/company.yml and customize it."
        )
    company_raw = _load_yaml(company_path)
    company = CompanyConfig(**company_raw.get("company", company_raw))

    # -- optional files (simple list-based configs) ------------------------
    _opt = _load_yaml_optional  # short alias

    simple_lists: dict[str, tuple[str, str, type[BaseModel]]] = {
        # field_name: (filename, yaml_key, model_class)
        "categories":     ("categories.yml",     "categories", CategoryConfig),
        "templates":      ("templates.yml",      "templates",  TemplateConfig),
        "knowledge_base": ("knowledge_base.yml", "categories", KBCategory),
        "business_rules": ("business_rules.yml", "rules",      BusinessRule),
        "locations":      ("locations.yml",      "locations",  LocationZone),
    }

    parsed_lists: dict[str, list[Any]] = {}
    for field, (filename, yaml_key, model_cls) in simple_lists.items():
        raw = _opt(config_dir / filename)
        parsed_lists[field] = _parse_list(raw, yaml_key, model_cls)

    # -- optional files (structured configs) -------------------------------
    sla_raw = _opt(config_dir / "sla.yml")
    asset_raw = _opt(config_dir / "assets.yml")
    sec_raw = _opt(config_dir / "security.yml")
    iso_raw = _opt(config_dir / "iso27001.yml")

    return ToolkitConfig(
        company=company,
        sla=_parse_sla(sla_raw),
        categories=parsed_lists["categories"],
        security=_parse_security(sec_raw),
        templates=parsed_lists["templates"],
        knowledge_base=parsed_lists["knowledge_base"],
        assets=AssetsConfig(**asset_raw) if asset_raw else AssetsConfig(),
        business_rules=parsed_lists["business_rules"],
        locations=parsed_lists["locations"],
        iso27001=_parse_iso27001(iso_raw),
    )
