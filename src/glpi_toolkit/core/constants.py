"""Shared constants — colors, ITIL v4 reference data, ISO 27001 category totals.

Color values are stored as plain hex strings.  Report modules (PDF / PPTX)
should convert them to framework-specific color objects (e.g. ``reportlab.lib.colors``
or ``pptx.util.Pt``) at the point of use.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Color palette (hex)
# ---------------------------------------------------------------------------

# Core UI / report palette
COLOR_DARK_BG = "#1a1a2e"
COLOR_DARK_SECONDARY = "#16213e"
COLOR_ACCENT = "#0f3460"
COLOR_HIGHLIGHT = "#e94560"
COLOR_SUCCESS = "#27ae60"
COLOR_WARNING = "#f39c12"
COLOR_INFO = "#3498db"
COLOR_DANGER = "#e74c3c"
COLOR_MUTED = "#95a5a6"

# Neutrals
COLOR_WHITE = "#ffffff"
COLOR_BLACK = "#000000"
COLOR_LIGHT_GRAY = "#f5f5f5"
COLOR_MEDIUM_GRAY = "#bdc3c7"
COLOR_DARK_GRAY = "#2c3e50"

# SLA priority colors (used in charts and dashboards)
PRIORITY_COLORS: dict[str, str] = {
    "critical": "#e74c3c",
    "high": "#e67e22",
    "normal": "#3498db",
    "low": "#27ae60",
}

# ISO 27001 control status colors
CONTROL_STATUS_COLORS: dict[str, str] = {
    "covered": "#27ae60",
    "partial": "#f39c12",
    "not_covered": "#e74c3c",
}

# Chart palette (8 distinct colors for pie/bar charts)
CHART_PALETTE: list[str] = [
    "#0f3460",
    "#e94560",
    "#27ae60",
    "#f39c12",
    "#3498db",
    "#9b59b6",
    "#1abc9c",
    "#e67e22",
]

# ---------------------------------------------------------------------------
# ITIL v4 reference data
# ---------------------------------------------------------------------------

ITIL_PRIORITY_ORDER: list[str] = ["critical", "high", "normal", "low"]

ITIL_TICKET_TYPES: dict[str, int] = {
    "incident": 1,
    "request": 2,
}

ITIL_TICKET_STATUS: dict[str, int] = {
    "new": 1,
    "processing_assigned": 2,
    "processing_planned": 3,
    "pending": 4,
    "solved": 5,
    "closed": 6,
}

ITIL_URGENCY: dict[str, int] = {
    "very_high": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "very_low": 1,
}

ITIL_IMPACT: dict[str, int] = {
    "very_high": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "very_low": 1,
}

# Priority matrix (urgency x impact -> priority label)
ITIL_PRIORITY_MATRIX: dict[tuple[int, int], str] = {
    # (urgency, impact) -> priority
    (5, 5): "critical",
    (5, 4): "critical",
    (4, 5): "critical",
    (5, 3): "high",
    (4, 4): "high",
    (3, 5): "high",
    (4, 3): "normal",
    (3, 4): "normal",
    (3, 3): "normal",
    (5, 2): "normal",
    (2, 5): "normal",
    (4, 2): "low",
    (3, 2): "low",
    (2, 4): "low",
    (2, 3): "low",
    (2, 2): "low",
    (5, 1): "low",
    (4, 1): "low",
    (3, 1): "low",
    (2, 1): "low",
    (1, 5): "low",
    (1, 4): "low",
    (1, 3): "low",
    (1, 2): "low",
    (1, 1): "low",
}

# GLPI item types used when talking to the REST API
GLPI_ITEM_TYPES: dict[str, str] = {
    "ticket": "Ticket",
    "computer": "Computer",
    "monitor": "Monitor",
    "printer": "Printer",
    "network_equipment": "NetworkEquipment",
    "phone": "Phone",
    "peripheral": "Peripheral",
    "software": "Software",
    "user": "User",
    "group": "Group",
    "entity": "Entity",
    "location": "Location",
    "category": "ITILCategory",
    "sla": "SLA",
    "ola": "OLA",
    "profile": "Profile",
    "document": "Document",
    "document_category": "DocumentCategory",
    "knowledge_base": "KnowbaseItem",
    "ticket_template": "TicketTemplate",
    "state": "State",
    "computer_type": "ComputerType",
    "software_category": "SoftwareCategory",
    "rule_ticket": "RuleTicket",
}

# ---------------------------------------------------------------------------
# ISO 27001:2022 Annex A — category totals
# ---------------------------------------------------------------------------
# Official control counts per ISO 27001:2022.  Used by the report generator
# to calculate coverage percentages even when only a subset of controls is
# mapped inside ``iso27001.yml``.

ISO27001_CATEGORY_TOTALS: dict[str, int] = {
    "organizational": 37,
    "people": 8,
    "physical": 14,
    "technological": 34,
}

ISO27001_TOTAL_CONTROLS: int = sum(ISO27001_CATEGORY_TOTALS.values())  # 93

ISO27001_CATEGORY_LABELS: dict[str, str] = {
    "organizational": "Organizational Controls (A.5)",
    "people": "People Controls (A.6)",
    "physical": "Physical Controls (A.7)",
    "technological": "Technological Controls (A.8)",
}

ISO27001_CATEGORY_RANGES: dict[str, str] = {
    "organizational": "A.5.1 - A.5.37",
    "people": "A.6.1 - A.6.8",
    "physical": "A.7.1 - A.7.14",
    "technological": "A.8.1 - A.8.34",
}
