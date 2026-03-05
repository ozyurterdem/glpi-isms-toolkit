# Getting Started

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (for GLPI deployment)
- pip or pipx

## Installation

### From PyPI (recommended)

```bash
pip install glpi-isms-toolkit
```

### From Source

```bash
git clone https://github.com/erdemozyurt/glpi-isms-toolkit.git
cd glpi-isms-toolkit
pip install -e .
```

## Deploy GLPI

1. Copy the environment file and set passwords:

```bash
cp .env.example .env
```

2. Generate strong passwords:

```bash
# Generate a strong password
openssl rand -base64 24
```

3. Edit `.env` with your passwords:

```env
GLPI_DB_ROOT_PASSWORD=your_strong_root_password
GLPI_DB_PASSWORD=your_strong_glpi_password
```

4. Start the stack:

```bash
docker compose up -d
```

5. Access GLPI at `http://localhost:80`

## Initialize Configuration

Choose a preset that matches your environment:

```bash
# Manufacturing / Factory
glpi-toolkit init --preset factory --company "Your Company"

# General Office
glpi-toolkit init --preset office --company "Your Company"
```

This creates a `config/` directory with pre-filled YAML files.

## Customize

Edit the YAML files in `config/` to match your organization:

- `company.yml` — Company name, branding, timezone
- `sla.yml` — SLA response/resolution times
- `categories.yml` — Helpdesk categories
- `security.yml` — Password policy, RBAC profiles
- `templates.yml` — Ticket templates
- `locations.yml` — Physical locations

## Generate Reports

```bash
# Both PDF and PPTX
glpi-toolkit report

# Specific format
glpi-toolkit report --format pdf --lang tr

# Custom output directory
glpi-toolkit report --output /path/to/output
```

## Run ISO 27001 Audit

```bash
# Print to console
glpi-toolkit iso-audit

# Save to file
glpi-toolkit iso-audit --output gap-report.txt
```

## Next Steps

- Read [Configuration Guide](configuration.md) for detailed YAML documentation
- Review [ISO 27001 Mapping](iso27001-mapping.md) for control details
- Deploy GLPI Agent to endpoints using the GPO script in `gpo/`
