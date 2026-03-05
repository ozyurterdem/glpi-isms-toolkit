"""ISO 27001:2022 Annex A — Complete Control Database.

Contains all 93 controls organized by the four categories defined in the 2022 revision:
  - Organizational controls (A.5): 37 controls
  - People controls (A.6): 8 controls
  - Physical controls (A.7): 14 controls
  - Technological controls (A.8): 34 controls
"""

from __future__ import annotations

# ── Full ISO 27001:2022 Annex A Control Database ──────────────────────────────

ISO27001_CONTROLS: list[dict[str, str]] = [
    # ══════════════════════════════════════════════════════════════════════════
    # A.5 — Organizational Controls (37)
    # ══════════════════════════════════════════════════════════════════════════
    {"id": "A.5.1",  "name": "Policies for Information Security",                "category": "organizational"},
    {"id": "A.5.2",  "name": "Information Security Roles and Responsibilities",  "category": "organizational"},
    {"id": "A.5.3",  "name": "Segregation of Duties",                            "category": "organizational"},
    {"id": "A.5.4",  "name": "Management Responsibilities",                      "category": "organizational"},
    {"id": "A.5.5",  "name": "Contact with Authorities",                         "category": "organizational"},
    {"id": "A.5.6",  "name": "Contact with Special Interest Groups",             "category": "organizational"},
    {"id": "A.5.7",  "name": "Threat Intelligence",                              "category": "organizational"},
    {"id": "A.5.8",  "name": "Information Security in Project Management",       "category": "organizational"},
    {"id": "A.5.9",  "name": "Inventory of Information and Other Associated Assets", "category": "organizational"},
    {"id": "A.5.10", "name": "Acceptable Use of Information and Other Associated Assets", "category": "organizational"},
    {"id": "A.5.11", "name": "Return of Assets",                                 "category": "organizational"},
    {"id": "A.5.12", "name": "Classification of Information",                    "category": "organizational"},
    {"id": "A.5.13", "name": "Labelling of Information",                         "category": "organizational"},
    {"id": "A.5.14", "name": "Information Transfer",                             "category": "organizational"},
    {"id": "A.5.15", "name": "Access Control",                                   "category": "organizational"},
    {"id": "A.5.16", "name": "Identity Management",                              "category": "organizational"},
    {"id": "A.5.17", "name": "Authentication Information",                       "category": "organizational"},
    {"id": "A.5.18", "name": "Access Rights",                                    "category": "organizational"},
    {"id": "A.5.19", "name": "Information Security in Supplier Relationships",   "category": "organizational"},
    {"id": "A.5.20", "name": "Addressing Information Security Within Supplier Agreements", "category": "organizational"},
    {"id": "A.5.21", "name": "Managing Information Security in the ICT Supply Chain", "category": "organizational"},
    {"id": "A.5.22", "name": "Monitoring, Review and Change Management of Supplier Services", "category": "organizational"},
    {"id": "A.5.23", "name": "Information Security for Use of Cloud Services",   "category": "organizational"},
    {"id": "A.5.24", "name": "Information Security Incident Management Planning and Preparation", "category": "organizational"},
    {"id": "A.5.25", "name": "Assessment and Decision on Information Security Events", "category": "organizational"},
    {"id": "A.5.26", "name": "Response to Information Security Incidents",       "category": "organizational"},
    {"id": "A.5.27", "name": "Learning from Information Security Incidents",     "category": "organizational"},
    {"id": "A.5.28", "name": "Collection of Evidence",                           "category": "organizational"},
    {"id": "A.5.29", "name": "Information Security During Disruption",           "category": "organizational"},
    {"id": "A.5.30", "name": "ICT Readiness for Business Continuity",            "category": "organizational"},
    {"id": "A.5.31", "name": "Legal, Statutory, Regulatory and Contractual Requirements", "category": "organizational"},
    {"id": "A.5.32", "name": "Intellectual Property Rights",                     "category": "organizational"},
    {"id": "A.5.33", "name": "Protection of Records",                            "category": "organizational"},
    {"id": "A.5.34", "name": "Privacy and Protection of PII",                    "category": "organizational"},
    {"id": "A.5.35", "name": "Independent Review of Information Security",       "category": "organizational"},
    {"id": "A.5.36", "name": "Compliance with Policies, Rules and Standards for Information Security", "category": "organizational"},
    {"id": "A.5.37", "name": "Documented Operating Procedures",                  "category": "organizational"},

    # ══════════════════════════════════════════════════════════════════════════
    # A.6 — People Controls (8)
    # ══════════════════════════════════════════════════════════════════════════
    {"id": "A.6.1", "name": "Screening",                                         "category": "people"},
    {"id": "A.6.2", "name": "Terms and Conditions of Employment",                "category": "people"},
    {"id": "A.6.3", "name": "Information Security Awareness, Education and Training", "category": "people"},
    {"id": "A.6.4", "name": "Disciplinary Process",                              "category": "people"},
    {"id": "A.6.5", "name": "Responsibilities After Termination or Change of Employment", "category": "people"},
    {"id": "A.6.6", "name": "Confidentiality or Non-Disclosure Agreements",      "category": "people"},
    {"id": "A.6.7", "name": "Remote Working",                                    "category": "people"},
    {"id": "A.6.8", "name": "Information Security Event Reporting",              "category": "people"},

    # ══════════════════════════════════════════════════════════════════════════
    # A.7 — Physical Controls (14)
    # ══════════════════════════════════════════════════════════════════════════
    {"id": "A.7.1",  "name": "Physical Security Perimeters",                     "category": "physical"},
    {"id": "A.7.2",  "name": "Physical Entry",                                   "category": "physical"},
    {"id": "A.7.3",  "name": "Securing Offices, Rooms and Facilities",           "category": "physical"},
    {"id": "A.7.4",  "name": "Physical Security Monitoring",                     "category": "physical"},
    {"id": "A.7.5",  "name": "Protecting Against Physical and Environmental Threats", "category": "physical"},
    {"id": "A.7.6",  "name": "Working in Secure Areas",                          "category": "physical"},
    {"id": "A.7.7",  "name": "Clear Desk and Clear Screen",                      "category": "physical"},
    {"id": "A.7.8",  "name": "Equipment Siting and Protection",                  "category": "physical"},
    {"id": "A.7.9",  "name": "Security of Assets Off-Premises",                  "category": "physical"},
    {"id": "A.7.10", "name": "Storage Media",                                    "category": "physical"},
    {"id": "A.7.11", "name": "Supporting Utilities",                             "category": "physical"},
    {"id": "A.7.12", "name": "Cabling Security",                                 "category": "physical"},
    {"id": "A.7.13", "name": "Equipment Maintenance",                            "category": "physical"},
    {"id": "A.7.14", "name": "Secure Disposal or Re-Use of Equipment",           "category": "physical"},

    # ══════════════════════════════════════════════════════════════════════════
    # A.8 — Technological Controls (34)
    # ══════════════════════════════════════════════════════════════════════════
    {"id": "A.8.1",  "name": "User Endpoint Devices",                            "category": "technological"},
    {"id": "A.8.2",  "name": "Privileged Access Rights",                         "category": "technological"},
    {"id": "A.8.3",  "name": "Information Access Restriction",                   "category": "technological"},
    {"id": "A.8.4",  "name": "Access to Source Code",                            "category": "technological"},
    {"id": "A.8.5",  "name": "Secure Authentication",                            "category": "technological"},
    {"id": "A.8.6",  "name": "Capacity Management",                              "category": "technological"},
    {"id": "A.8.7",  "name": "Protection Against Malware",                       "category": "technological"},
    {"id": "A.8.8",  "name": "Management of Technical Vulnerabilities",          "category": "technological"},
    {"id": "A.8.9",  "name": "Configuration Management",                         "category": "technological"},
    {"id": "A.8.10", "name": "Information Deletion",                              "category": "technological"},
    {"id": "A.8.11", "name": "Data Masking",                                      "category": "technological"},
    {"id": "A.8.12", "name": "Data Leakage Prevention",                           "category": "technological"},
    {"id": "A.8.13", "name": "Information Backup",                                "category": "technological"},
    {"id": "A.8.14", "name": "Redundancy of Information Processing Facilities",   "category": "technological"},
    {"id": "A.8.15", "name": "Logging",                                           "category": "technological"},
    {"id": "A.8.16", "name": "Monitoring Activities",                              "category": "technological"},
    {"id": "A.8.17", "name": "Clock Synchronization",                             "category": "technological"},
    {"id": "A.8.18", "name": "Use of Privileged Utility Programs",                "category": "technological"},
    {"id": "A.8.19", "name": "Installation of Software on Operational Systems",   "category": "technological"},
    {"id": "A.8.20", "name": "Networks Security",                                 "category": "technological"},
    {"id": "A.8.21", "name": "Security of Network Services",                      "category": "technological"},
    {"id": "A.8.22", "name": "Segregation of Networks",                            "category": "technological"},
    {"id": "A.8.23", "name": "Web Filtering",                                     "category": "technological"},
    {"id": "A.8.24", "name": "Use of Cryptography",                               "category": "technological"},
    {"id": "A.8.25", "name": "Secure Development Life Cycle",                     "category": "technological"},
    {"id": "A.8.26", "name": "Application Security Requirements",                 "category": "technological"},
    {"id": "A.8.27", "name": "Secure System Architecture and Engineering Principles", "category": "technological"},
    {"id": "A.8.28", "name": "Secure Coding",                                     "category": "technological"},
    {"id": "A.8.29", "name": "Security Testing in Development and Acceptance",    "category": "technological"},
    {"id": "A.8.30", "name": "Outsourced Development",                            "category": "technological"},
    {"id": "A.8.31", "name": "Separation of Development, Test and Production Environments", "category": "technological"},
    {"id": "A.8.32", "name": "Change Management",                                 "category": "technological"},
    {"id": "A.8.33", "name": "Test Information",                                  "category": "technological"},
    {"id": "A.8.34", "name": "Protection of Information Systems During Audit Testing", "category": "technological"},
]

# Category display names for reports
CATEGORY_LABELS: dict[str, str] = {
    "organizational": "Organizational Controls (A.5)",
    "people": "People Controls (A.6)",
    "physical": "Physical Controls (A.7)",
    "technological": "Technological Controls (A.8)",
}

# Expected totals per ISO 27001:2022
CATEGORY_TOTALS: dict[str, int] = {
    "organizational": 37,
    "people": 8,
    "physical": 14,
    "technological": 34,
}


def get_all_controls() -> list[dict[str, str]]:
    """Return the complete list of 93 ISO 27001:2022 Annex A controls."""
    return list(ISO27001_CONTROLS)


def get_controls_by_category(category: str) -> list[dict[str, str]]:
    """Return controls filtered by category.

    Args:
        category: One of 'organizational', 'people', 'physical', 'technological'.

    Returns:
        List of control dicts matching the given category.

    Raises:
        ValueError: If the category is not recognized.
    """
    valid_categories = {"organizational", "people", "physical", "technological"}
    if category not in valid_categories:
        raise ValueError(
            f"Unknown category '{category}'. Must be one of: {', '.join(sorted(valid_categories))}"
        )
    return [c for c in ISO27001_CONTROLS if c["category"] == category]


def get_category_totals() -> dict[str, int]:
    """Return the expected control count per category.

    Returns:
        Dict mapping category names to their total control count:
        ``{'organizational': 37, 'people': 8, 'physical': 14, 'technological': 34}``
    """
    return dict(CATEGORY_TOTALS)
