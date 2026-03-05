"""GLPI ISMS Toolkit — Command-line interface.

Entry point registered as ``glpi-toolkit`` in pyproject.toml.
Uses Typer for argument parsing and Rich for formatted console output.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from glpi_toolkit import __version__

# ── Typer app ─────────────────────────────────────────────────────────────────

app = typer.Typer(
    name="glpi-toolkit",
    help="GLPI ISMS Toolkit — configuration-as-code for GLPI with ISO 27001 integration.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_config_dir(config: Path) -> Path:
    """Resolve and validate a config directory path."""
    path = config.resolve()
    if not path.is_dir():
        err_console.print(f"[red]Error:[/red] Config directory not found: {path}")
        raise typer.Exit(code=1)
    return path


def _load_yaml(filepath: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    if not filepath.is_file():
        err_console.print(f"[red]Error:[/red] File not found: {filepath}")
        raise typer.Exit(code=1)
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return {}
        return data
    except yaml.YAMLError as exc:
        err_console.print(f"[red]YAML parse error[/red] in {filepath.name}: {exc}")
        raise typer.Exit(code=1)


def _load_company_config(config_dir: Path) -> dict:
    """Load company.yml from the config directory."""
    return _load_yaml(config_dir / "company.yml")


def _ensure_output_dir(output: Path) -> Path:
    """Create the output directory if it does not exist."""
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    return output


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"glpi-isms-toolkit v{__version__}")
        raise typer.Exit()


# ── Global options ────────────────────────────────────────────────────────────

@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """GLPI ISMS Toolkit — configuration-as-code for GLPI with ISO 27001 integration."""


# ══════════════════════════════════════════════════════════════════════════════
# report
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def report(
    format: str = typer.Option(
        "both",
        "--format",
        "-f",
        help="Output format: pdf, pptx, or both.",
    ),
    config: Path = typer.Option(
        Path("./config"),
        "--config",
        "-c",
        help="Path to the config directory.",
    ),
    output: Path = typer.Option(
        Path("./output"),
        "--output",
        "-o",
        help="Output directory for generated reports.",
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Report language override (en or tr). Defaults to config value.",
    ),
) -> None:
    """Generate PDF and/or PPTX executive reports from configuration."""
    config_dir = _resolve_config_dir(config)
    output_dir = _ensure_output_dir(output)

    # Determine language
    company = _load_company_config(config_dir)
    language = lang or company.get("company", {}).get("language", "en")
    company_name = company.get("company", {}).get("name", "Unknown")

    valid_formats = {"pdf", "pptx", "both"}
    if format not in valid_formats:
        err_console.print(f"[red]Error:[/red] --format must be one of: {', '.join(valid_formats)}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold]Report Generation[/bold]\n\n"
            f"  Company:  {company_name}\n"
            f"  Format:   {format}\n"
            f"  Language: {language}\n"
            f"  Config:   {config_dir}\n"
            f"  Output:   {output_dir}",
            title="glpi-toolkit",
            border_style="blue",
        )
    )

    formats_to_generate: list[str] = []
    if format == "both":
        formats_to_generate = ["pdf", "pptx"]
    else:
        formats_to_generate = [format]

    for fmt in formats_to_generate:
        with console.status(f"[bold blue]Generating {fmt.upper()} report..."):
            try:
                if fmt == "pdf":
                    from glpi_toolkit.reports.pdf import generate_pdf
                    outfile = output_dir / f"{company_name.lower().replace(' ', '_')}_report.pdf"
                    generate_pdf(config_dir=config_dir, output_path=outfile, language=language)
                    console.print(f"  [green]PDF saved:[/green] {outfile}")
                elif fmt == "pptx":
                    from glpi_toolkit.reports.pptx import generate_pptx
                    outfile = output_dir / f"{company_name.lower().replace(' ', '_')}_report.pptx"
                    generate_pptx(config_dir=config_dir, output_path=outfile, language=language)
                    console.print(f"  [green]PPTX saved:[/green] {outfile}")
            except ImportError:
                err_console.print(
                    f"  [yellow]Warning:[/yellow] {fmt.upper()} report module not yet implemented. Skipping."
                )
            except Exception as exc:
                err_console.print(f"  [red]Error generating {fmt.upper()}:[/red] {exc}")

    console.print("\n[bold green]Done.[/bold green]")


# ══════════════════════════════════════════════════════════════════════════════
# iso-audit
# ══════════════════════════════════════════════════════════════════════════════

@app.command("iso-audit")
def iso_audit(
    config: Path = typer.Option(
        Path("./config"),
        "--config",
        "-c",
        help="Path to the config directory.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save report to file instead of printing to console.",
    ),
) -> None:
    """Run ISO 27001:2022 gap analysis against your GLPI configuration."""
    config_dir = _resolve_config_dir(config)

    from glpi_toolkit.core.config import load_config
    from glpi_toolkit.iso27001.mapper import ISO27001Mapper

    toolkit_config = load_config(config_dir)
    mapper = ISO27001Mapper(toolkit_config.iso27001)

    # ── Summary table ─────────────────────────────────────────────────────
    summary = mapper.get_coverage_summary()
    overall = mapper.get_overall_percentage()

    table = Table(title="ISO 27001:2022 — Coverage Summary", show_lines=True)
    table.add_column("Category", style="bold")
    table.add_column("Total", justify="right")
    table.add_column("Covered", justify="right", style="green")
    table.add_column("Partial", justify="right", style="yellow")
    table.add_column("Gaps", justify="right", style="red")
    table.add_column("Coverage", justify="right")

    for cat_data in summary.values():
        pct = cat_data["percentage"]
        pct_style = "green" if pct >= 60 else ("yellow" if pct >= 30 else "red")
        table.add_row(
            cat_data["label"],
            str(cat_data["total"]),
            str(cat_data["covered"]),
            str(cat_data["partial"]),
            str(cat_data["uncovered"]),
            Text(f"{pct}%", style=pct_style),
        )

    # Totals row
    total_covered = sum(d["covered"] for d in summary.values())
    total_partial = sum(d["partial"] for d in summary.values())
    total_uncovered = sum(d["uncovered"] for d in summary.values())
    overall_style = "green" if overall >= 60 else ("yellow" if overall >= 30 else "red")
    table.add_row(
        "[bold]TOTAL[/bold]",
        "[bold]93[/bold]",
        f"[bold]{total_covered}[/bold]",
        f"[bold]{total_partial}[/bold]",
        f"[bold]{total_uncovered}[/bold]",
        Text(f"{overall}%", style=f"bold {overall_style}"),
    )

    console.print()
    console.print(table)
    console.print()

    # ── Full text report (save or display) ────────────────────────────────
    report_text = mapper.generate_gap_report()

    if output:
        output_path = output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding="utf-8")
        console.print(f"[green]Full report saved to:[/green] {output_path}")
    else:
        console.print(
            Panel(
                report_text,
                title="Gap Analysis Report",
                border_style="cyan",
                expand=True,
            )
        )


# ══════════════════════════════════════════════════════════════════════════════
# init
# ══════════════════════════════════════════════════════════════════════════════

PRESETS = {
    "factory": {
        "industry": "manufacturing",
        "description": "Manufacturing / factory environment with production IT",
    },
    "office": {
        "industry": "office",
        "description": "General office / corporate environment",
    },
    "startup": {
        "industry": "startup",
        "description": "Lean startup with cloud-first approach",
    },
}


@app.command()
def init(
    preset: str = typer.Option(
        "factory",
        "--preset",
        "-p",
        help="Configuration preset: factory, office, or startup.",
    ),
    company: str = typer.Option(
        ...,
        "--company",
        "-n",
        help="Company name for the configuration.",
        prompt="Company name",
    ),
) -> None:
    """Initialize a new config directory from a preset template."""
    if preset not in PRESETS:
        err_console.print(
            f"[red]Error:[/red] Unknown preset '{preset}'. "
            f"Available: {', '.join(PRESETS.keys())}"
        )
        raise typer.Exit(code=1)

    config_dir = Path("./config")
    if config_dir.exists() and any(config_dir.iterdir()):
        overwrite = typer.confirm(
            f"Config directory '{config_dir}' already exists. Overwrite?",
            default=False,
        )
        if not overwrite:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()

    config_dir.mkdir(parents=True, exist_ok=True)

    # Copy preset example if it exists, otherwise create company.yml
    preset_meta = PRESETS[preset]
    preset_file = Path(__file__).parent.parent.parent / "config" / "examples" / f"{preset}.yml"

    if preset_file.is_file():
        shutil.copy(preset_file, config_dir / "company.yml")
        console.print(f"  [green]Copied preset:[/green] {preset}.yml -> config/company.yml")
    else:
        # Generate a minimal company.yml
        company_config = {
            "company": {
                "name": company,
                "short_name": company.split()[0] if company else "Co",
                "department": "IT Department",
                "industry": preset_meta["industry"],
                "timezone": "Europe/Istanbul",
                "language": "en",
                "confidentiality": "Internal — Confidential",
                "report": {
                    "author": "IT Department",
                    "version": "1.0",
                    "date_format": "%B %d, %Y",
                },
                "branding": {
                    "primary": "#1a1a2e",
                    "secondary": "#16213e",
                    "accent": "#0f3460",
                    "highlight": "#e94560",
                    "success": "#27ae60",
                    "warning": "#f39c12",
                },
            }
        }
        with open(config_dir / "company.yml", "w", encoding="utf-8") as f:
            yaml.dump(company_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        console.print("  [green]Created:[/green] config/company.yml")

    # Patch the company name into the copied file
    company_yml = config_dir / "company.yml"
    if company_yml.is_file():
        content = company_yml.read_text(encoding="utf-8")
        # Replace the preset default name with the user-provided name
        for placeholder in ["Acme Manufacturing", "Acme Office Corp", "Acme Startup"]:
            content = content.replace(placeholder, company)
        short = company.split()[0] if company else "Co"
        content = content.replace('short_name: "Acme"', f'short_name: "{short}"')
        company_yml.write_text(content, encoding="utf-8")

    # Copy remaining config files from the package's config directory
    package_config = Path(__file__).parent.parent.parent / "config"
    config_files = [
        "iso27001.yml",
        "security.yml",
        "sla.yml",
        "categories.yml",
        "assets.yml",
        "locations.yml",
        "templates.yml",
        "knowledge_base.yml",
        "business_rules.yml",
    ]
    for cfg_file in config_files:
        src = package_config / cfg_file
        dst = config_dir / cfg_file
        if src.is_file() and not dst.is_file():
            shutil.copy(src, dst)
            console.print(f"  [green]Copied:[/green] {cfg_file}")
        elif dst.is_file():
            console.print(f"  [dim]Skipped (exists):[/dim] {cfg_file}")

    console.print()
    console.print(
        Panel(
            f"[bold green]Configuration initialized![/bold green]\n\n"
            f"  Preset:  {preset} — {preset_meta['description']}\n"
            f"  Company: {company}\n"
            f"  Path:    {config_dir.resolve()}\n\n"
            f"Next steps:\n"
            f"  1. Edit config/company.yml with your organization details\n"
            f"  2. Customize config/iso27001.yml with your control mappings\n"
            f"  3. Run: [bold]glpi-toolkit validate[/bold]\n"
            f"  4. Run: [bold]glpi-toolkit iso-audit[/bold]",
            title="glpi-toolkit init",
            border_style="green",
        )
    )


# ══════════════════════════════════════════════════════════════════════════════
# validate
# ══════════════════════════════════════════════════════════════════════════════

REQUIRED_CONFIG_FILES = [
    "company.yml",
    "iso27001.yml",
    "security.yml",
    "sla.yml",
    "categories.yml",
    "assets.yml",
    "locations.yml",
]

REQUIRED_COMPANY_KEYS = ["name", "department", "industry", "language"]


@app.command()
def validate(
    config: Path = typer.Option(
        Path("./config"),
        "--config",
        "-c",
        help="Path to the config directory.",
    ),
) -> None:
    """Validate configuration files for completeness and correctness."""
    config_dir = _resolve_config_dir(config)

    errors: list[str] = []
    warnings: list[str] = []
    passed: list[str] = []

    # ── Check required files ──────────────────────────────────────────────
    for filename in REQUIRED_CONFIG_FILES:
        filepath = config_dir / filename
        if not filepath.is_file():
            errors.append(f"Missing required file: {filename}")
        else:
            try:
                data = _load_yaml(filepath)
                if not data:
                    warnings.append(f"{filename} is empty")
                else:
                    passed.append(f"{filename} — valid YAML")
            except SystemExit:
                errors.append(f"{filename} — invalid YAML syntax")

    # ── Validate company.yml structure ────────────────────────────────────
    company_path = config_dir / "company.yml"
    if company_path.is_file():
        company_data = _load_yaml(company_path)
        company_section = company_data.get("company", {})
        for key in REQUIRED_COMPANY_KEYS:
            if key not in company_section:
                errors.append(f"company.yml: missing 'company.{key}'")
            else:
                passed.append(f"company.yml: company.{key} present")

        lang = company_section.get("language", "")
        if lang and lang not in ("en", "tr", "de"):
            warnings.append(f"company.yml: language '{lang}' may not have full string support")

    # ── Validate iso27001.yml ─────────────────────────────────────────────
    iso_path = config_dir / "iso27001.yml"
    if iso_path.is_file():
        iso_data = _load_yaml(iso_path)
        controls = iso_data.get("controls", [])
        if not controls:
            warnings.append("iso27001.yml: no controls defined")
        else:
            passed.append(f"iso27001.yml: {len(controls)} controls mapped")

            # Check for valid statuses
            valid_statuses = {"covered", "partial", "not_covered", "uncovered"}
            for ctrl in controls:
                ctrl_id = ctrl.get("id", "???")
                status = ctrl.get("status", "")
                if status and status not in valid_statuses:
                    errors.append(
                        f"iso27001.yml: control {ctrl_id} has invalid status '{status}'"
                    )

    # ── Validate SLA ──────────────────────────────────────────────────────
    sla_path = config_dir / "sla.yml"
    if sla_path.is_file():
        sla_data = _load_yaml(sla_path)
        levels = sla_data.get("sla", {}).get("levels", {})
        if not levels:
            warnings.append("sla.yml: no SLA levels defined")
        else:
            passed.append(f"sla.yml: {len(levels)} SLA levels configured")

    # ── Validate security.yml ─────────────────────────────────────────────
    sec_path = config_dir / "security.yml"
    if sec_path.is_file():
        sec_data = _load_yaml(sec_path)
        pw = sec_data.get("password_policy", {})
        if pw:
            min_len = pw.get("min_length", 0)
            if min_len < 8:
                warnings.append(
                    f"security.yml: password min_length is {min_len} (ISO 27001 recommends >= 8)"
                )
            else:
                passed.append(f"security.yml: password policy OK (min {min_len} chars)")

    # ── Display results ───────────────────────────────────────────────────
    console.print()

    table = Table(title="Configuration Validation", show_lines=False)
    table.add_column("Status", width=8)
    table.add_column("Detail")

    for msg in passed:
        table.add_row("[green]PASS[/green]", msg)
    for msg in warnings:
        table.add_row("[yellow]WARN[/yellow]", msg)
    for msg in errors:
        table.add_row("[red]FAIL[/red]", msg)

    console.print(table)
    console.print()

    if errors:
        console.print(
            f"[bold red]Validation failed[/bold red] with {len(errors)} error(s) "
            f"and {len(warnings)} warning(s)."
        )
        raise typer.Exit(code=1)
    elif warnings:
        console.print(
            f"[bold yellow]Validation passed[/bold yellow] with {len(warnings)} warning(s)."
        )
    else:
        console.print("[bold green]All checks passed.[/bold green]")


# ══════════════════════════════════════════════════════════════════════════════
# logo
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def logo(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Company name for the generated logo.",
        prompt="Company name",
    ),
    output: Path = typer.Option(
        Path("./output"),
        "--output",
        "-o",
        help="Output directory for branding assets.",
    ),
    theme: str = typer.Option(
        "dark",
        "--theme",
        "-t",
        help="Color theme: dark, light, or grey.",
    ),
) -> None:
    """Generate branding assets (logo, sidebar, icon, favicon) for GLPI."""
    output_dir = _ensure_output_dir(output)

    try:
        from glpi_toolkit.branding.generator import LogoGenerator
    except ImportError:
        err_console.print("[red]Error:[/red] Pillow is required. Install with: pip install Pillow")
        raise typer.Exit(code=1)

    with console.status("[bold blue]Generating branding assets..."):
        gen = LogoGenerator(name, str(output_dir))
        outputs = gen.generate_all(theme=theme)

    for asset_name, path in outputs.items():
        console.print(f"  [green]{asset_name}:[/green] {path}")

    console.print("\n[bold green]Branding assets generated.[/bold green]")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
