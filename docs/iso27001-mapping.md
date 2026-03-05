# ISO 27001:2022 Control Mapping

## Overview

ISO 27001:2022 Annex A contains **93 controls** organized into 4 categories:

| Category | Controls | Description |
|----------|----------|-------------|
| A.5 Organizational | 37 | Policies, roles, asset management, incident handling |
| A.6 People | 8 | Screening, employment, termination |
| A.7 Physical | 14 | Physical security, equipment, utilities |
| A.8 Technological | 34 | Endpoint, authentication, network, crypto |

## Default Coverage

The toolkit's default configuration covers approximately **27%** of all controls through GLPI configurations and ISMS document integration.

### Covered Controls

#### Organizational (A.5) — 15 of 37

| Control | Name | GLPI Implementation |
|---------|------|---------------------|
| A.5.1 | Information Security Policies | Document module stores ISMS policies |
| A.5.2 | Information Security Roles | 5-profile RBAC structure |
| A.5.3 | Segregation of Duties | Profile-based permission isolation |
| A.5.9 | Inventory of Assets | ITAM with automated discovery |
| A.5.10 | Acceptable Use of Assets | Asset state tracking |
| A.5.11 | Return of Assets | Offboarding process |
| A.5.15 | Access Control Policy | Least privilege, RBAC |
| A.5.16 | Identity Management | Onboarding/offboarding workflow |
| A.5.17 | Authentication Information | Password policy enforcement |
| A.5.18 | Access Rights | Periodic access review |
| A.5.23 | Cloud Services Security | On-premise hosting |
| A.5.24 | Incident Management Planning | ITIL ticket system |
| A.5.25 | Assessment of Security Events | Priority classification |
| A.5.26 | Response to Incidents | 4-tier SLA with escalation |
| A.5.37 | Documented Procedures | Knowledge base articles |

#### People (A.6) — 4 of 8

| Control | Name | GLPI Implementation |
|---------|------|---------------------|
| A.6.1 | Screening | Onboarding checklist |
| A.6.2 | Terms of Employment | Policy signing tracking |
| A.6.4 | Disciplinary Process | Policy violation template |
| A.6.5 | Termination Responsibilities | Offboarding checklist |

#### Physical (A.7) — 1 of 14

| Control | Name | GLPI Implementation |
|---------|------|---------------------|
| A.7.1 | Physical Security Perimeters | Location hierarchy |

#### Technological (A.8) — 5 of 34

| Control | Name | GLPI Implementation |
|---------|------|---------------------|
| A.8.1 | User Endpoint Devices | PC/laptop inventory |
| A.8.5 | Secure Authentication | Password complexity/lockout |
| A.8.9 | Configuration Management | Equipment config records |
| A.8.20 | Network Security | VLAN segmentation docs |
| A.8.21 | Network Services Security | Guest isolation (partial) |

## Extending Coverage

To increase your ISO 27001 coverage:

1. **Phase 4: Log Management** (+A.8.15, A.8.16) — Deploy SIEM/centralized logging
2. **Phase 5: Encryption** (+A.8.24) — Implement disk/email encryption
3. **Phase 6: Backup** (+A.8.13) — Formalize backup procedures
4. **Phase 7: Physical Security** (+A.7.x) — Access control systems

Edit `config/iso27001.yml` to add newly covered controls and re-run `glpi-toolkit iso-audit`.
