# Configuration Guide

All configuration is stored in YAML files under the `config/` directory. This guide covers each file in detail.

## company.yml

Core company information used across all reports and outputs.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company.name` | string | Yes | Full company name |
| `company.short_name` | string | No | Abbreviated name |
| `company.department` | string | Yes | Department generating reports |
| `company.industry` | string | No | Industry type for presets |
| `company.timezone` | string | Yes | IANA timezone |
| `company.language` | string | Yes | Default language (en/tr) |
| `company.branding.*` | hex | No | Color overrides |

## sla.yml

SLA and OLA definitions based on ITIL v4.

Each SLA level requires:
- `name` — Display name
- `response` — Maximum response time (e.g., "1h", "4h", "24h")
- `resolution` — Maximum resolution time (e.g., "8h", "3d", "5d")
- `examples` — List of example scenarios

Time format: `{number}{unit}` where unit is `h` (hours) or `d` (business days).

## security.yml

Maps to ISMS-POL-002 (Password Policy) and ISO 27001 A.5.15-A.5.18.

### Password Policy

| Field | Default | Description |
|-------|---------|-------------|
| `min_length` | 10 | Minimum password length |
| `require_uppercase` | true | At least one uppercase letter |
| `require_number` | true | At least one digit |
| `require_symbol` | true | At least one special character |
| `expiry_days` | 90 | Password expiry period |
| `max_attempts` | 5 | Failed attempts before lockout |
| `lockout_minutes` | 30 | Lockout duration |

### RBAC Profiles

Define user profiles with permission levels. The `is_default` profile is assigned to new users (least privilege principle — ISO A.5.15).

## categories.yml

Hierarchical ITIL service categories. Each category has:
- `name` — Category name
- `type` — "incident" or "request"
- `subcategories` — List of child categories with default priority and assigned group
- `isms_ref` — Optional ISMS document reference

## iso27001.yml

Maps GLPI configurations to ISO 27001:2022 Annex A controls.

Each control entry:
- `id` — Control identifier (e.g., "A.5.1")
- `name` — Control name
- `category` — organizational / people / physical / technological
- `glpi_mapping` — How GLPI addresses this control
- `isms_ref` — Related ISMS document
- `status` — "covered", "partial", or "not_covered"

Run `glpi-toolkit iso-audit` to see your coverage percentage.
