# GLPI ISMS Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GLPI 11.x](https://img.shields.io/badge/GLPI-11.x-green.svg)](https://glpi-project.org/)
[![ISO 27001:2022](https://img.shields.io/badge/ISO_27001-2022-orange.svg)](https://www.iso.org/standard/27001)

**Configuration-as-code toolkit for GLPI with ISO 27001 ISMS integration.**

Bootstrap a fully configured GLPI ITSM platform from YAML files. Includes ITIL v4 SLA definitions, ISO 27001 control mapping, ISMS document integration, executive report generation (PDF + PPTX), and gap analysis — all without writing a single line of code.

---

## Features

| Feature | Description |
|---------|-------------|
| **YAML-Driven Config** | Define your entire GLPI setup in human-readable YAML files |
| **ISO 27001 Gap Analysis** | Map GLPI configurations to all 93 Annex A controls |
| **ISMS Integration** | Password policy, RBAC, user lifecycle aligned with ISMS documents |
| **Executive Reports** | Auto-generate PDF reports and PPTX presentations |
| **ITIL v4 SLA** | Pre-configured 4-tier SLA with global standard thresholds |
| **Ticket Templates** | 22 pre-defined templates including security and lifecycle |
| **Knowledge Base** | 18 article definitions for security awareness and IT procedures |
| **Branding** | Auto-generate logos, favicons, and theme assets |
| **Presets** | Ready-to-use configs for factory, office, and startup environments |
| **i18n** | English and Turkish language support |

## Quick Start

### 1. Install

```bash
pip install glpi-isms-toolkit
```

Or from source:

```bash
git clone https://github.com/erdemozyurt/glpi-isms-toolkit.git
cd glpi-isms-toolkit
pip install -e .
```

### 2. Deploy GLPI

```bash
cp .env.example .env
# Edit .env with strong passwords (openssl rand -base64 24)
docker compose up -d
```

### 3. Initialize Configuration

```bash
# Start with a preset
glpi-toolkit init --preset factory --company "Your Company"

# Or customize YAML files in config/ directly
```

### 4. Generate Reports

```bash
# Generate both PDF and PPTX
glpi-toolkit report --config ./config --output ./output

# PDF only
glpi-toolkit report --format pdf --lang tr

# PPTX only
glpi-toolkit report --format pptx --lang en
```

### 5. Run ISO 27001 Audit

```bash
# Console output
glpi-toolkit iso-audit --config ./config

# Export to file
glpi-toolkit iso-audit --config ./config --output gap-report.txt
```

## Project Structure

```
glpi-isms-toolkit/
├── config/                    # YAML configuration (customize these)
│   ├── company.yml            # Company info and branding
│   ├── sla.yml                # SLA/OLA definitions (ITIL v4)
│   ├── categories.yml         # ITIL service categories
│   ├── security.yml           # Password policy, RBAC profiles
│   ├── templates.yml          # Ticket templates
│   ├── knowledge_base.yml     # KB article definitions
│   ├── business_rules.yml     # Automatic routing rules
│   ├── locations.yml          # Physical location hierarchy
│   ├── assets.yml             # Asset states, types, categories
│   ├── iso27001.yml           # ISO control mapping
│   └── examples/
│       └── factory.yml        # Manufacturing preset
│
├── src/glpi_toolkit/          # Python source
│   ├── cli.py                 # CLI interface (typer)
│   ├── core/                  # Config loader, API client
│   ├── reports/               # PDF and PPTX generators
│   │   ├── pdf/
│   │   │   ├── builder.py     # PDF orchestrator
│   │   │   ├── styles.py      # ReportLab styles
│   │   │   ├── components.py  # Reusable components
│   │   │   └── sections/      # One file per report section
│   │   └── pptx/
│   │       ├── builder.py     # PPTX orchestrator
│   │       ├── theme.py       # Slide theme
│   │       └── components.py  # Slide helpers
│   ├── iso27001/              # ISO control database + mapper
│   └── branding/              # Logo and favicon generator
│
├── templates/                 # i18n string templates
│   ├── strings_en.yml
│   └── strings_tr.yml
│
├── docker-compose.yml         # GLPI + MariaDB stack
├── gpo/                       # Windows GPO scripts
└── docs/                      # Documentation
```

## Configuration

All configuration lives in YAML files under `config/`. Edit these files to match your organization — no Python knowledge required.

### Company (`config/company.yml`)

```yaml
company:
  name: "Your Company Name"
  department: "IT Department"
  industry: "manufacturing"     # manufacturing | office | healthcare | education
  timezone: "Europe/Istanbul"
  language: "en"                # en | tr
```

### SLA Levels (`config/sla.yml`)

Default values follow ITIL v4 global maximum thresholds:

| Level | Response | Resolution | Examples |
|-------|----------|------------|----------|
| Critical (P1) | 1 hour | 8 hours | Server down, data breach |
| High (P2) | 4 hours | 24 hours | Printer failure, VPN issue |
| Normal (P3) | 8 hours | 3 days | Software install, onboarding |
| Low (P4) | 24 hours | 5 days | Hardware request |

### Security (`config/security.yml`)

Maps directly to ISMS-POL-002 (Password Policy):

```yaml
password_policy:
  min_length: 10
  require_uppercase: true
  require_number: true
  require_symbol: true
  expiry_days: 90
  max_attempts: 5
  lockout_minutes: 30
```

### ISO 27001 Controls (`config/iso27001.yml`)

Map your GLPI configurations to ISO 27001:2022 Annex A controls:

```yaml
controls:
  - id: "A.5.17"
    name: "Authentication Information"
    glpi_mapping: "Password policy (complexity, expiry, lockout)"
    isms_ref: "ISMS-POL-002"
    status: "covered"    # covered | partial | not_covered
```

## ISO 27001 Coverage

Out of the box, this toolkit covers **25 of 93** Annex A controls (~27%):

| Category | Total | Covered | Percentage |
|----------|-------|---------|------------|
| Organizational (A.5) | 37 | 15 | 41% |
| People (A.6) | 8 | 4 | 50% |
| Physical (A.7) | 14 | 1 | 7% |
| Technological (A.8) | 34 | 5 | 15% |
| **Total** | **93** | **25** | **~27%** |

Run `glpi-toolkit iso-audit` to see your specific coverage and identify gaps.

## ISMS Documents

The toolkit integrates with three ISMS document types:

| Document | Purpose | GLPI Impact |
|----------|---------|-------------|
| **ISMS-POL-001** | Information Security Policy | Security categories, RBAC, KB articles |
| **ISMS-POL-002** | Password Policy | Password settings, lockout, ticket template |
| **ISMS-PRO-002** | User Lifecycle Procedure | Onboarding/offboarding templates, access review |

## CLI Reference

```
Usage: glpi-toolkit [COMMAND] [OPTIONS]

Commands:
  report      Generate executive reports (PDF/PPTX)
  iso-audit   Run ISO 27001 gap analysis
  init        Initialize config from preset
  validate    Validate configuration files
  logo        Generate branding assets

Options:
  --help      Show help message
  --version   Show version
```

## Docker Stack

The included `docker-compose.yml` deploys:

- **MariaDB 10.11** — GLPI database
- **GLPI 11.x** — ITSM/ITAM platform

```bash
cp .env.example .env
# Set GLPI_DB_ROOT_PASSWORD and GLPI_DB_PASSWORD
docker compose up -d
```

Access GLPI at `http://localhost:80`

## Security

- All credentials are managed via `.env` (never committed)
- `.gitignore` blocks `.env`, `*.pem`, `*.key`, and credential files
- Generated reports (PDF/PPTX) are excluded from version control
- No company-specific data in the repository
- RBAC profiles enforce least-privilege access

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/erdemozyurt/glpi-isms-toolkit.git
cd glpi-isms-toolkit
pip install -e ".[dev]"
pytest
ruff check src/
```

## Roadmap

- [ ] GLPI API provisioner (apply config via REST API)
- [ ] Hospital / healthcare preset
- [ ] Education / university preset
- [ ] Automated gap analysis with remediation suggestions
- [ ] GLPI plugin for real-time ISO 27001 dashboard
- [ ] Multi-language report support (DE, AR, FR)
- [ ] CI/CD pipeline templates

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [GLPI Project](https://glpi-project.org/) — Open-source ITSM/ITAM platform
- [ISO 27001:2022](https://www.iso.org/standard/27001) — Information security standard
- [ITIL v4](https://www.axelos.com/best-practice-solutions/itil) — IT service management framework

---

**Built with by [SiberKale](https://siberkale.com)**
